from codepass.llm.a_score_parser import FileAScoreEvaluation, FunctionAScoreEvaluation
from codepass.llm.model import file_a_score_model, improvement_suggestion_a_score_model
from codepass.token_budget_estimator import TokenBudgetEstimator
from dataclasses import dataclass, field
from typing import List, Dict, Any
from codepass.read_code_files import CodeFile
from langchain_core.exceptions import OutputParserException
from codepass.get_config import CodepassConfig


MAX_RETRIES = 1


@dataclass
class AScoreEvaluationResult:
    file_path: str
    line_count: int
    a_score: int
    improvement_suggestions: str

    error_message: str = ""

    details: Dict[str, Dict[Any, Any]] = field(default_factory=dict)


def file_line_count(function_complexities: List[FunctionAScoreEvaluation]) -> int:
    return sum(
        [
            function_complexity.line_count()
            for function_complexity in function_complexities
        ]
    )


def compute_file_a_score(
    function_complexities: List[FunctionAScoreEvaluation],
) -> float:
    return sum(
        [
            function_complexity.a_score_per_line()
            for function_complexity in function_complexities
        ]
    )


def compute_function_a_score(
    function_complexity: FunctionAScoreEvaluation,
) -> float:
    line_count = function_complexity.line_count()
    if line_count == 0:
        return 0
    return round(function_complexity.a_score_per_line() / line_count, 2)


def evaluate_a_score(
    code_file: CodeFile,
    token_budget_estimator: TokenBudgetEstimator,
    config: CodepassConfig,
) -> AScoreEvaluationResult:
    error_recovery_instructions = ""
    for _ in range(MAX_RETRIES):
        try:
            token_budget_estimator.await_budget(code_file)
            file_evaluation: FileAScoreEvaluation = file_a_score_model.invoke(
                {
                    "code": code_file.code,
                    "error_recovery_instructions": error_recovery_instructions,
                }
            )
            number_of_lines = file_line_count(file_evaluation.function_complexities)

            if number_of_lines == 0 or file_evaluation.number_of_functions == 0:
                return AScoreEvaluationResult(
                    file_path=code_file.path,
                    line_count=0,
                    a_score=0,
                    improvement_suggestions="",
                )

            if file_evaluation.number_of_functions != len(
                file_evaluation.function_complexities
            ):
                error_recovery_instructions = f"Number of functions detected in the file does not match the number of function evaluations."
                continue

            complexity_score = compute_file_a_score(
                file_evaluation.function_complexities
            )
            a_score = round(complexity_score / number_of_lines, 2)

            if (
                a_score > config.a_score_threshold
                and config.improvement_suggestions_enabled
            ):
                token_budget_estimator.await_budget(code_file)
                improvement_suggestions = improvement_suggestion_a_score_model.invoke(
                    {
                        "code": code_file.code,
                        "error_recovery_instructions": error_recovery_instructions,
                    }
                )
            else:
                improvement_suggestions = ""

            return AScoreEvaluationResult(
                line_count=number_of_lines,
                a_score=a_score,
                file_path=code_file.path,
                improvement_suggestions=improvement_suggestions,
                details={
                    function_complexity.function_name: {
                        "line_count": function_complexity.line_count(),
                        "score": compute_function_a_score(function_complexity),
                        "description": function_complexity.score_estimation_description,
                    }
                    for function_complexity in file_evaluation.function_complexities
                },
            )
        except OutputParserException as e:
            if error_recovery_instructions == "":
                error_recovery_instructions = "Be very careful in output formatting!"
            else:
                error_recovery_instructions = f"Parsing of output formatting already due to {str(e)}, please, avoid this issue again!"
    return AScoreEvaluationResult(
        file_path=code_file.path,
        line_count=0,
        a_score=0,
        improvement_suggestions="",
        error_message=error_recovery_instructions,
    )
