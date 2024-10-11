from codepass.llm.b_score_parser import (
    FileBScoreEvaluation,
    FunctionBScoreEvaluation,
)
from codepass.llm.model import file_b_score_model
from codepass.token_budget_estimator import TokenBudgetEstimator
from dataclasses import dataclass, field
from typing import List, Dict, Any
from codepass.read_code_files import CodeFile

from codepass.get_config import CodepassConfig
from codepass.llm.model import improvement_suggestion_b_score_model
from langchain_core.exceptions import OutputParserException

MAX_RETRIES = 1


@dataclass
class BScoreEvaluationResult:
    file_path: str
    line_count: int
    b_score: int

    error_message: str = ""
    improvement_suggestions: str = ""

    details: Dict[str, Dict[Any, Any]] = field(default_factory=dict)


def line_count(function_complexities: List[FunctionBScoreEvaluation]) -> int:
    return sum(
        [
            function_complexity.line_count()
            for function_complexity in function_complexities
        ]
    )


def compute_file_b_score(
    function_complexities: List[FunctionBScoreEvaluation],
) -> float:
    return sum(
        [
            function_complexity.b_score_per_line()
            for function_complexity in function_complexities
        ]
    )


def compute_function_b_score(
    function_complexity: FunctionBScoreEvaluation,
) -> float:
    line_count = function_complexity.line_count()
    if line_count == 0:
        return 0
    return round(function_complexity.b_score_per_line() / line_count, 2)


def evaluate_b_score(
    code_file: CodeFile,
    token_budget_estimator: TokenBudgetEstimator,
    config: CodepassConfig,
) -> BScoreEvaluationResult:
    error_recovery_instructions = ""
    for _ in range(MAX_RETRIES):
        try:
            token_budget_estimator.await_budget(code_file)
            file_evaluation: FileBScoreEvaluation = file_b_score_model.invoke(
                {
                    "code": code_file.code,
                    "error_recovery_instructions": error_recovery_instructions,
                }
            )
            number_of_lines = line_count(
                file_evaluation.function_abstraction_level_evaluations
            )

            if number_of_lines == 0 or file_evaluation.number_of_functions == 0:
                return BScoreEvaluationResult(
                    file_path=code_file.path,
                    line_count=0,
                    b_score=0,
                )

            if file_evaluation.number_of_functions != len(
                file_evaluation.function_abstraction_level_evaluations
            ):
                error_recovery_instructions = f"Number of functions detected in the file does not match the number of function evaluations."
                continue

            abstraction_level = compute_file_b_score(
                file_evaluation.function_abstraction_level_evaluations
            )

            b_score = round(abstraction_level / number_of_lines, 2)

            if (
                b_score > config.b_score_threshold
                and config.improvement_suggestions_enabled
            ):
                token_budget_estimator.await_budget(code_file)
                improvement_suggestions = improvement_suggestion_b_score_model.invoke(
                    {
                        "code": code_file.code,
                        "error_recovery_instructions": error_recovery_instructions,
                    }
                )
            else:
                improvement_suggestions = ""

            return BScoreEvaluationResult(
                line_count=number_of_lines,
                b_score=b_score,
                file_path=code_file.path,
                improvement_suggestions=improvement_suggestions,
                details={
                    function_complexity.function_name: {
                        "line_count": function_complexity.line_count(),
                        "score": compute_function_b_score(function_complexity),
                        "description": function_complexity.score_estimation_description,
                    }
                    for function_complexity in file_evaluation.function_abstraction_level_evaluations
                },
            )
        except OutputParserException as e:
            if error_recovery_instructions == "":
                error_recovery_instructions = "Be very careful in output formatting!"
            else:
                error_recovery_instructions = f"Parsing of output formatting already due to {str(e)}, please, avoid this issue again!"
    return BScoreEvaluationResult(
        file_path=code_file.path,
        line_count=0,
        b_score=0,
        error_message=error_recovery_instructions,
    )
