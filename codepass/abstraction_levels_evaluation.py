from codepass.parsers import (
    FileAbstractionEvaluation,
    FunctionAbstractionLevels,
    FunctionAbstractionLevels,
    AbstractionLevelPriority,
    AbstractionLevelEstimation,
)
from codepass.model import file_abstraction_levels
from codepass.token_budget_estimator import TokenBudgetEstimator
from dataclasses import dataclass
from typing import List
from codepass.read_code_files import CodeFile


@dataclass
class AbstractionEvaluationResult:
    file_path: str
    line_count: int
    b_score: int

    b_score_error_message: str = ""


def is_abstraction_level_significant(
    abstraction_level: AbstractionLevelEstimation,
) -> bool:
    return (
        abstraction_level.confidence > 0.75
        and abstraction_level.priority
        > AbstractionLevelPriority.does_not_affect_core_behavior
    )


def estimate_abstraction_level(
    function_abstraction_level_evaluations: FunctionAbstractionLevels,
) -> int:
    abstraction_levels_int = set(
        [
            int(level.abstraction_level)
            for level in function_abstraction_level_evaluations.abstraction_levels
            if is_abstraction_level_significant(level)
        ]
    )
    estimated_abstraction_level = max(len(abstraction_levels_int), 1)
    return (
        estimated_abstraction_level
        * function_abstraction_level_evaluations.count_lines()
    )


def line_count(function_complexities: List[FunctionAbstractionLevels]) -> int:
    return sum(
        [
            function_complexity.count_lines()
            for function_complexity in function_complexities
        ]
    )


def complexity_score(function_complexities: List[FunctionAbstractionLevels]) -> int:
    return sum(
        [
            function_complexity.complexity_score_impact()
            for function_complexity in function_complexities
        ]
    )


def evaluate_abstraction_levels(
    code_file: CodeFile, token_budget_estimator: TokenBudgetEstimator
) -> AbstractionEvaluationResult:
    error_recovery_instructions = ""
    for _ in range(3):
        try:
            token_budget_estimator.await_budget(code_file)
            file_evaluation: FileAbstractionEvaluation = file_abstraction_levels.invoke(
                {
                    "code": code_file.code,
                    "error_recovery_instructions": error_recovery_instructions,
                }
            )
            number_of_lines = line_count(
                file_evaluation.function_abstraction_level_evaluations
            )

            if number_of_lines == 0 or file_evaluation.number_of_functions == 0:
                return AbstractionEvaluationResult(
                    file_path=code_file.path,
                    line_count=0,
                    b_score=0,
                )

            abstraction_level = sum(
                [
                    estimate_abstraction_level(fun)
                    for fun in file_evaluation.function_abstraction_level_evaluations
                ]
            )

            b_score = round(abstraction_level / number_of_lines, 2)

            return AbstractionEvaluationResult(
                line_count=number_of_lines,
                b_score=b_score,
                file_path=code_file.path,
            )
        except Exception as e:
            error_recovery_instructions = (
                f"Attempt to process the files was interrupted due to {str(e)}"
            )
    return AbstractionEvaluationResult(
        file_path=code_file.path,
        line_count=0,
        b_score=0,
        b_score_error_message=error_recovery_instructions,
    )
