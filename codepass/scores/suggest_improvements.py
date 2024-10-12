from codepass.llm.improvement_suggestion_parser import ImprovementSuggestion
from codepass.llm.model import improvement_suggestion_model
from codepass.token_budget_estimator import TokenBudgetEstimator
from dataclasses import dataclass, field
from typing import List, Dict, Any
from codepass.read_code_files import CodeFile
from langchain_core.exceptions import OutputParserException
from codepass.get_config import CodepassConfig


MAX_RETRIES = 7


@dataclass
class ImprovementSuggestionResult:
    file_path: str
    start_line: 0
    end_line: 0
    improvement_suggestion: str

    error_message: str = ""


def suggest_improvements(
    code_file: CodeFile,
    token_budget_estimator: TokenBudgetEstimator,
) -> ImprovementSuggestionResult:
    error_recovery_instructions = ""
    for _ in range(MAX_RETRIES):
        try:
            token_budget_estimator.await_budget(code_file)
            improvement_suggestion: ImprovementSuggestion = (
                improvement_suggestion_model.invoke(
                    {
                        "code": code_file.code,
                        "error_recovery_instructions": error_recovery_instructions,
                    }
                )
            )

            return ImprovementSuggestionResult(
                file_path=code_file.path,
                start_line=improvement_suggestion.start_line_number,
                end_line=improvement_suggestion.end_line_number,
                improvement_suggestion=improvement_suggestion.improvement_suggestion,
                error_message="",
            )
        except OutputParserException as e:
            if error_recovery_instructions == "":
                error_recovery_instructions = "Be very careful in output formatting!"
            else:
                error_recovery_instructions = f"Parsing of output formatting already due to {str(e)}, please, avoid this issue again!"
    return ImprovementSuggestionResult(
        file_path=code_file.path,
        improvement_suggestions="",
        error_message=error_recovery_instructions,
    )
