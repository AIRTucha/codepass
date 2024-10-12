from importlib.metadata import version
from codepass.read_code_files import read_files, CodeFile

from codepass.token_budget_estimator import TokenBudgetEstimator
from codepass.scores.evaluate_a_score import evaluate_a_score
from codepass.scores.evaluate_b_score import evaluate_b_score
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


OPEN_AI_TOKEN_LIMIT_PER_MINUTE = 200 * 1000
MAX_TOKENS_PER_FILE = 100 * 1000


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
        lambda file: file.token_count < MAX_TOKENS_PER_FILE,
    )

    (_, changed_files) = partition(
        accepted_files,
        lambda file: file.path in report_files
        and report_files[file.path].hash == file.hash
        and not config.clear,
    )
    return (changed_files, large_files)


def run_evaluation(changed_files: List[CodeFile], config: CodepassConfig):
    parallel_runtime = ParallelRuntime()
    token_budget_estimator = TokenBudgetEstimator(OPEN_AI_TOKEN_LIMIT_PER_MINUTE)

    if config.a_score_enabled:
        for code_file in changed_files:
            parallel_runtime.add_task(
                evaluate_a_score, code_file, token_budget_estimator, config
            )

    if config.b_score_enabled:
        for code_file in changed_files:
            parallel_runtime.add_task(
                evaluate_b_score, code_file, token_budget_estimator, config
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
    return round(total_a_score / total_lines, 2)


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
    return round(total_b_score / total_lines, 2)


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
        report["recommendation_count"] = sum(
            1 for f in report_files_list if f.improvement_suggestions != ""
        )

    if config.b_score_enabled:
        report["b_score"] = aggregate_b_score(report_files_list)

    report["files"] = [file.__dict__ for file in report_files_list]

    return report


def save_report(report):
    with open("codepass.report.json", "w") as f:
        f.write(
            dumps(
                report,
                indent=4,
            )
        )


def print_improvement_suggestions(report_files_list):
    print()
    print(Fore.YELLOW + "Improvement Suggestions: ")
    print()
    report_files_list.sort(key=lambda x: x.a_score, reverse=True)
    for file in report_files_list:
        if file.improvement_suggestions:
            print(Fore.YELLOW + "File:", file.file_path)
            print()
            print(Fore.GREEN + "Suggestion:", file.improvement_suggestions)
            print()


async def main():
    start = time.time()
    config = get_config()

    if validate_config(config):
        print("No analysis enabled")
        return

    code_files = read_files(config.paths, config.ignore_files)
    report_files = get_report_files(code_files)

    (changed_files, large_files) = combine_report_and_files(
        config, code_files, report_files
    )

    print(Fore.GREEN + "Analyzing files:", len(code_files))
    print(Fore.GREEN + "Changed files:", len(changed_files))
    print(
        Fore.GREEN + f"Estimated token count: {upper_estimate_token_count(code_files)}"
    )

    complexity_result = run_evaluation(changed_files, config)

    report_files_list = combine_report_files(
        config,
        complexity_result,
        changed_files,
        large_files,
        report_files,
    )

    end = time.time()

    report = aggregate_report(report_files_list, config)

    print()
    if report.get("a_score", 0) > 0:
        print(f"A score: {report['a_score']}")
    if report.get("b_score", 0) > 0:
        print(f"B score: {report['b_score']}")

    print(f"Done:", f"{str(round(end - start, 1))}s")

    save_report(report)

    if (
        config.print_improvement_suggestions
        and report.get("recommendation_count", 0) > 0
    ):
        print_improvement_suggestions(report_files_list)

    if config.a_score_enabled and report.get("a_score", 0) > config.a_score_threshold:
        print(Fore.RED + "A score is too high")
        exit(1)

    if config.b_score_enabled and report.get("b_score", 0) > config.b_score_threshold:
        print(Fore.RED + "B score is too high")
        exit(1)


def run_main():
    asyncio.run(main())
