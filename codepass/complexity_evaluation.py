from codepass.parsers import FileComplexityEvaluation, FunctionComplexityEvaluation
from codepass.model import file_complexity
from codepass.token_budget_estimator import TokenBudgetEstimator
from dataclasses import dataclass
from typing import List
from codepass.read_code_files import CodeFile


@dataclass
class ComplexityEvaluationResult:
    file_path: str
    line_count: int
    a_score: int
    improvement_suggestions: str

    a_score_error_message: str = ""


def line_count(function_complexities: List[FunctionComplexityEvaluation]) -> int:
    return sum(
        [
            function_complexity.count_lines()
            for function_complexity in function_complexities
        ]
    )


def compute_complexity_score(
    function_complexities: List[FunctionComplexityEvaluation],
) -> int:
    return sum(
        [
            function_complexity.complexity_score_impact()
            for function_complexity in function_complexities
        ]
    )


def evaluate_file_complexity(
    code_file: CodeFile, token_budget_estimator: TokenBudgetEstimator
) -> ComplexityEvaluationResult:
    error_recovery_instructions = ""
    for _ in range(3):
        try:
            token_budget_estimator.await_budget(code_file)
            file_evaluation: FileComplexityEvaluation = file_complexity.invoke(
                {
                    "code": code_file.code,
                    "error_recovery_instructions": error_recovery_instructions,
                }
            )
            number_of_lines = line_count(file_evaluation.function_complexities)

            if number_of_lines == 0 or file_evaluation.number_of_functions == 0:
                return ComplexityEvaluationResult(
                    file_path=code_file.path,
                    line_count=0,
                    a_score=0,
                    improvement_suggestions="",
                )

            complexity_score = compute_complexity_score(
                file_evaluation.function_complexities
            )
            a_score = round(complexity_score / number_of_lines, 2)

            return ComplexityEvaluationResult(
                line_count=number_of_lines,
                a_score=a_score,
                file_path=code_file.path,
                improvement_suggestions=file_evaluation.improvement_suggestions,
            )
        except Exception as e:
            error_message = (
                f"Attempt to process the files was interrupted due to {str(e)}"
            )
    return ComplexityEvaluationResult(
        file_path=code_file.path,
        line_count=0,
        a_score=0,
        improvement_suggestions="",
        error_message=error_message,
    )
