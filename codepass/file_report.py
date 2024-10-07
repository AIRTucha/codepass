from codepass.abstraction_levels_evaluation import AbstractionEvaluationResult
from codepass.complexity_evaluation import ComplexityEvaluationResult
from codepass.read_code_files import CodeFile


class FileReport:
    line_count: int | None = None
    improvement_suggestions = ""

    def __init__(self, file_path: str, hash: str):
        self.file_path = file_path
        self.hash = hash

    def add_data(
        self,
        report: ComplexityEvaluationResult | AbstractionEvaluationResult,
        a_score_threshold: float,
    ):
        self.line_count = (
            report.line_count
            if self.line_count is None
            else max(self.line_count, report.line_count)
        )

        if isinstance(report, ComplexityEvaluationResult):
            self.a_score = report.a_score
            self.a_score_error_message = report.a_score_error_message
            self.improvement_suggestions = (
                report.improvement_suggestions
                if report.a_score > a_score_threshold
                else ""
            )
        else:
            self.b_score = report.b_score
            self.b_score_error_message = report.b_score_error_message

    def mark_as_large(self, code_file: CodeFile, a_score: bool, b_score: bool):
        if a_score:
            self.a_score = 5
            self.a_score_error_message = "File is too large to evaluate"
            self.improvement_suggestions = "Breakdown into smaller files"

        if b_score:
            self.b_score = 5
            self.b_score_error_message = "File is too large to evaluate"

        self.line_count = code_file.code.count("\n")

    def load_from_dict(data: dict):

        report = FileReport("", "")
        report.__dict__.update(data)
        return report
