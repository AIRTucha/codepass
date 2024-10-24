from importlib.metadata import version
from codepass.read_code_files import read_files, CodeFile

from codepass.token_budget_estimator import TokenBudgetEstimator
from codepass.scores.evaluate_a_score import evaluate_a_score
from codepass.scores.evaluate_b_score import evaluate_b_score
from codepass.scores.suggest_improvements import suggest_improvements
from codepass.file_report import FileReport
from codepass.parallel_runtime import ParallelRuntime
from codepass.utils import partition
from codepass.get_report_file import get_report_files

import asyncio

from colorama import Fore

import time

from codepass.get_config import get_config, CodepassConfig
import time
from typing import Dict, List
from json import dumps


def score_absolute_difference(a: float, b: float) -> float:
    return abs(a - b)


def upper_estimate_token_count(code_files: List[CodeFile]):
    return int(sum([file.token_count for file in code_files]) * 1.5)


def validate_config(config: CodepassConfig):
    return not config.a_score_enabled and not config.b_score_enabled


def combine_report_and_files(
    config: CodepassConfig,
    code_files: List[CodeFile],
    report_files: Dict[str, FileReport],
):
    (accepted_files, large_files) = partition(
        code_files,
        lambda file: file.token_count < config.max_context_size,
    )

    (_, changed_files) = partition(
        accepted_files,
        lambda file: file.path in report_files
        and report_files[file.path].hash == file.hash
        and not config.clear,
    )
    return (changed_files, large_files)


def run_evaluation(
    token_budget_estimator, changed_files: List[CodeFile], config: CodepassConfig
):
    parallel_runtime = ParallelRuntime(token_budget_estimator)

    analyze_files = changed_files.copy()

    analyze_files.sort(key=lambda file: file.token_count, reverse=True)

    if config.a_score_enabled:
        for code_file in analyze_files:
            parallel_runtime.add_task(
                code_file.token_count,
                evaluate_a_score,
                code_file,
                config.model_name,
                token_budget_estimator,
            )

    if config.b_score_enabled:
        for code_file in analyze_files:
            parallel_runtime.add_task(
                code_file.token_count,
                evaluate_b_score,
                code_file,
                config.model_name,
                token_budget_estimator,
            )

    return parallel_runtime.run_tasks()


def combine_report_files(
    config, complexity_result, changed_files, large_files, report_files
):
    new_report_files: Dict[str, FileReport] = {
        result.path: FileReport(result.path, result.hash) for result in changed_files
    }

    for large_file in large_files:
        if large_file.path not in report_files:
            report_files[large_file.path] = FileReport(large_file.path, large_file.hash)
        report_files[large_file.path].mark_as_large(large_file, config)

    for result in complexity_result:
        new_report_files[result.file_path].add_data(result, config)

    report_files.update(new_report_files)

    return list(report_files.values())


def aggregate_a_score(report_files_list: List[FileReport]):
    total_lines = sum(
        [
            f.line_count
            for f in report_files_list
            if (hasattr(f, "a_score") and f.a_score > 0)
        ]
    )

    if total_lines == 0:
        return 0

    total_a_score = sum([f.a_score * f.line_count for f in report_files_list])
    return round(total_a_score / total_lines, 1)


def aggregate_b_score(report_files_list: List[FileReport]):
    total_lines = sum(
        [
            f.line_count
            for f in report_files_list
            if (hasattr(f, "b_score") and f.b_score > 0)
        ]
    )

    if total_lines == 0:
        return 0

    total_b_score = sum([f.b_score * f.line_count for f in report_files_list])
    return round(total_b_score / total_lines, 1)


def aggregate_report(
    report_files_list: List[FileReport],
    config: CodepassConfig,
):
    file_count = len(report_files_list)
    report = {
        "file_count": file_count,
        "version": version("codepass"),
    }

    if config.a_score_enabled:
        report["a_score"] = aggregate_a_score(report_files_list)

    if config.b_score_enabled:
        report["b_score"] = aggregate_b_score(report_files_list)

    report["recommendation_count"] = sum(
        1 for f in report_files_list if hasattr(f, "improvement_suggestion")
    )

    report["files"] = [file.__dict__ for file in report_files_list]

    return report


def is_improvement_needed(config, result) -> bool:
    if (
        config.a_score_enabled
        and hasattr(result, "a_score")
        and result.a_score > config.a_score_threshold
    ):
        return True

    if (
        config.b_score_enabled
        and hasattr(result, "b_score")
        and result.b_score > config.b_score_threshold
    ):
        return True

    return False


def generate_suggestion_improvement(
    config, token_budget_estimator, complexity_result, changed_files, report_files
):
    need_improvements_file_names = set(
        result.file_path
        for result in complexity_result
        if is_improvement_needed(config, result)
    )
    need_improvements_files = [
        file for file in changed_files if file.path in need_improvements_file_names
    ]

    if len(need_improvements_files) == 0:
        return

    print("Generating improvement suggestions")

    parallel_runtime = ParallelRuntime(token_budget_estimator)

    for code_file in need_improvements_files:
        parallel_runtime.add_task(
            code_file.token_count,
            suggest_improvements,
            code_file,
            config.model_name,
            token_budget_estimator,
        )

    suggestion_improvements = parallel_runtime.run_tasks()

    for suggestion in suggestion_improvements:
        report_files[suggestion.file_path].add_improvement_suggestions(suggestion)


def save_report(report):
    with open("codepass.report.json", "w") as f:
        f.write(
            dumps(
                report,
                indent=4,
            )
        )


def sort_by_score(report):
    if hasattr(report, "a_score"):
        return report.a_score
    if hasattr(report, "b_score"):
        return report.b_score

    return 0


def print_improvement_suggestions(report_files_list):
    print()
    print(Fore.YELLOW + "Improvement Suggestions: ")
    print()
    report_files_list.sort(key=sort_by_score, reverse=True)
    for file in report_files_list:
        if hasattr(file, "improvement_suggestion"):
            print(Fore.YELLOW + "File:", file.file_path)
            if hasattr(file, "a_score"):
                print(Fore.YELLOW + "A Score:", file.a_score)
            if hasattr(file, "b_score"):
                print(Fore.YELLOW + "B Score:", file.b_score)

            print(
                Fore.GREEN + "Suggestion:",
                file.improvement_suggestion.get("description"),
            )
            print()


def print_errors(report_files_list):
    error_count = sum(1 for f in report_files_list if hasattr(f, "error_message"))
    if error_count == 0:
        return

    print()
    print(Fore.RED + "Errors: ")
    print()
    report_files_list.sort(key=sort_by_score, reverse=True)
    for file in report_files_list:
        if hasattr(file, "error_message"):
            print(Fore.YELLOW + "File:", file.file_path)
            print()
            print(
                Fore.RED + "Error Message:",
                file.error_message,
            )
            print()


async def main():
    start = time.time()
    config = get_config()

    if config.print_version:
        print(version("codepass"))
        exit(0)

    if validate_config(config):
        print("No analysis enabled")
        return

    code_files = read_files(config.paths, config.ignore_files)
    previous_report = get_report_files(code_files)

    report_files = previous_report.files

    (changed_files, large_files) = combine_report_and_files(
        config, code_files, report_files
    )

    print(Fore.GREEN + "Analyzing files:", len(code_files))
    print(Fore.GREEN + "Changed files:", len(changed_files))
    print(
        Fore.GREEN + f"Estimated token count: {upper_estimate_token_count(code_files)}"
    )
    print("Evaluate scores")
    token_budget_estimator = TokenBudgetEstimator(config.token_rate_limit)
    complexity_result = run_evaluation(token_budget_estimator, changed_files, config)

    report_files_list = combine_report_files(
        config,
        complexity_result,
        changed_files,
        large_files,
        report_files,
    )

    if config.improvement_suggestions_enabled:
        generate_suggestion_improvement(
            config,
            token_budget_estimator,
            complexity_result,
            changed_files,
            report_files,
        )

    end = time.time()

    report = aggregate_report(report_files_list, config)

    print()
    if report.get("a_score", 0) > 0:
        if (
            previous_report.a_score != None
            and score_absolute_difference(report["a_score"], previous_report.a_score)
            > 0.1
        ):
            if report["a_score"] > previous_report.a_score:
                print(
                    "A score:",
                    report["a_score"],
                    Fore.GREEN
                    + f"({round(previous_report.a_score - report['a_score'], 1)})",
                )
            else:
                print(
                    "A score:",
                    report["a_score"],
                    Fore.RED
                    + f"+({round(previous_report.a_score - report['a_score'], 1)})",
                )
        else:
            print("A score:", report["a_score"])
    if report.get("b_score", 0) > 0:
        if (
            previous_report.b_score != None
            and score_absolute_difference(report["b_score"], previous_report.b_score)
            > 0.1
        ):
            if report["b_score"] > previous_report.b_score:
                print(
                    Fore.GREEN + "B score:",
                    report["b_score"],
                    Fore.GREEN
                    + f"({round(previous_report.b_score - report['b_score'], 1)})",
                )
            else:
                print(
                    Fore.GREEN + "B score:",
                    report["b_score"],
                    Fore.RED
                    + f"+({round(previous_report.b_score - report['b_score'],1)})",
                )
        else:
            print(Fore.GREEN + "B score:", report["b_score"])

    print(Fore.GREEN + f"Done:", f"{str(round(end - start, 1))}s")

    save_report(report)

    if (
        config.print_improvement_suggestions
        and report.get("recommendation_count", 0) > 0
    ):
        print_improvement_suggestions(report_files_list)

    if config.error_info_enabled:
        print_errors(report_files_list)

    if config.a_score_enabled and report.get("a_score", 0) > config.a_score_threshold:
        print(Fore.RED + "A score is too high")
        exit(1)

    if config.b_score_enabled and report.get("b_score", 0) > config.b_score_threshold:
        print(Fore.RED + "B score is too high")
        exit(1)


def run_main():
    asyncio.run(main())
