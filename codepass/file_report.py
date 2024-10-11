from codepass.get_config import CodepassConfig
from codepass.scores.evaluate_a_score import AScoreEvaluationResult
from codepass.scores.evaluate_b_score import BScoreEvaluationResult
from codepass.read_code_files import CodeFile
from dataclasses import asdict


class FileReport:
    line_count: int = 0
    improvement_suggestions = ""

    def __init__(self, file_path: str, hash: str):
        self.file_path = file_path
        self.hash = hash

    def _add_error_message(
        self,
        report: AScoreEvaluationResult | BScoreEvaluationResult,
        is_error_enabled: bool,
    ):
        if is_error_enabled and report.error_message:
            if self.error_message:
                self.error_message = self.error_message + "\n\n" + report.error_message
            else:
                self.error_message = report.error_message

    def _add_improvement_suggestions(
        self,
        report: AScoreEvaluationResult | BScoreEvaluationResult,
        is_improvement_suggestions_enabled: bool,
    ):
        if is_improvement_suggestions_enabled and report.improvement_suggestions:
            if self.improvement_suggestions:
                self.improvement_suggestions = (
                    self.improvement_suggestions
                    + "\n\n"
                    + report.improvement_suggestions
                )
            else:
                self.improvement_suggestions = report.improvement_suggestions

    def add_data(
        self,
        report: AScoreEvaluationResult | BScoreEvaluationResult,
        config: CodepassConfig,
    ):
        self.line_count = (self.line_count + report.line_count) / 2

        if isinstance(report, AScoreEvaluationResult):
            self.a_score = report.a_score
            if config.details_enabled:
                self.a_score_details = report.details
        else:
            self.b_score = report.b_score
            if config.details_enabled:
                self.b_score_details = report.details

        self._add_error_message(report, config.error_info_enabled)
        self._add_improvement_suggestions(
            report, config.improvement_suggestions_enabled
        )

    def mark_as_large(
        self,
        code_file: CodeFile,
        config: CodepassConfig,
    ):
        if config.a_score_enabled:
            self.a_score = 0

        if config.b_score_enabled:
            self.b_score = 0

        if config.error_info_enabled:
            self.error_message = "File is too large to evaluate"

        if config.improvement_suggestions_enabled:
            self.improvement_suggestions = "Breakdown into smaller files"

        self.line_count = code_file.code.count("\n")

    def load_from_dict(data: dict):
        try:
            report = FileReport("", "")
            report.__dict__.update(data)
            return report
        except:
            return {}
