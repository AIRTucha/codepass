from langchain.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field

from typing import List
import math

from pydantic import BaseModel, Field

SCORE_MIN_VALUE = 1
SCORE_MAX_VALUE = 5
SCORE_RANGE_VALUE = SCORE_MAX_VALUE - SCORE_MIN_VALUE


class FunctionAScoreEvaluation(BaseModel):
    function_name: str = Field(description="Name of the function")

    is_setup_of_declaration: bool = Field(
        description="The code is part of setup or declaration boilerplate, such as defining constants or configuring a framework."
    )

    readability_score: float = Field(
        description="Estimate how readable the code is based on factors like naming conventions, formatting, and non-runtime characteristics.\n\
        Score ranges:\n\
        0 - 0.3: The code follows standard naming conventions, is well-formatted, and lacks clutter (e.g., no magic numbers or excessive boilerplate).\n\
        0.3 - 0.7: Minor readability issues, inconsistent formatting, occasional use of names under 3 letter long, or slight violations of coding standards.\n\
        0.7 - 1: Significant readability problems, non-standard conventions, inconsistent formatting, completely unclear names and control structures."
    )

    cognitive_complexity_score: float = Field(
        description="Estimate the cognitive complexity of control structures and expressions.\n\
        Score ranges:\n\
        0 - 0.3: From simple to moderate control structures (some nesting, straightforward logic, few operators).\n\
        0.3 - 0.7: Highly complexity, deep nesting (3+), complex boolean/arithmetic expressions.\n\
        0.7 - 1: Very high complexity of control slot, intricate logic with many operators and brackets, or multiple conditional/loop combinations."
    )

    project_specific_knowledge_score: float = Field(
        description="Estimate how much project-specific knowledge is required, such as the use of third-party libraries or specific business rules.\n\
        Score ranges:\n\
        0 - 0.3: Little to no project-specific knowledge required, uses common third-party libraries or standard business rules.\n\
        0.3 - 0.7: Some project-specific knowledge is needed, involving custom libraries or moderately complex business rules.\n\
        0.7 - 1: Extensive project-specific knowledge required, highly customized third-party libraries or intricate, specific business logic."
    )

    technical_domain_knowledge_score: float = Field(
        description="Estimate the level of deep technical domain knowledge required, such as advanced algorithms, parallel programming, signal processing, or low-level optimizations.\n\
        Score ranges:\n\
        0 - 0.3: Minimal technical domain knowledge required, standard algorithms and techniques used.\n\
        0.3 - 0.7: Moderate technical domain knowledge, involving specialized algorithms, parallel programming, or some scientific/engineering calculations.\n\
        0.7 - 1: High level of technical domain knowledge required, including advanced algorithms, low-level optimizations, or complex scientific/mathematical concepts."
    )

    advanced_code_techniques_score: float = Field(
        description="Estimate the use of advanced coding techniques (like functional programming paradigms) that are not essential for solving the task but reflect the developer’s preference.\n\
        Score ranges:\n\
        0 - 0.3: No or minimal use of advanced techniques, the code is straightforward and easy to follow.\n\
        0.3 - 0.7: Some use of advanced techniques (e.g., functional programming, reactive programming) that increase complexity but do not dominate the code.\n\
        0.7 - 1: Heavy use of advanced techniques that significantly add complexity without being essential for solving the problem (e.g., monads, currying, category theory)."
    )

    start_line_number: int = Field(
        description="Number of the first line of the function, considering existing formatting"
    )

    end_line_number: int = Field(
        description="Number of the last line of the function, considering existing formatting"
    )

    def line_count(self) -> int:
        if self.is_setup_of_declaration:
            return 0
        return self.end_line_number - self.start_line_number

    def _mean_weighted_linear_complexity_score(self) -> float:
        linear_weighted_advanced_programming_techniques_usage = (
            5 * self.advanced_code_techniques_score
        )
        linear_weighted_technical_domain_expertise_usage = (
            4 * self.technical_domain_knowledge_score
        )
        linear_weighted_algorithms_usage = 3 * self.project_specific_knowledge_score
        linear_weighted_computation_usage = 2 * self.cognitive_complexity_score
        linear_weighted_project_specific_knowledge_usage = 1 * self.readability_score

        return (
            sum(
                [
                    linear_weighted_advanced_programming_techniques_usage,
                    linear_weighted_technical_domain_expertise_usage,
                    linear_weighted_algorithms_usage,
                    linear_weighted_computation_usage,
                    linear_weighted_project_specific_knowledge_usage,
                ]
            )
            / 15
        )

    def _normalized_mean_correction_sum_weighted_sq_complexity_score(self) -> float:
        linear_mean = self._mean_weighted_linear_complexity_score()

        if linear_mean == 0:
            return 0

        weighted_advanced_programming_techniques_usage = 5 * math.pow(
            self.advanced_code_techniques_score, 2
        )
        weighted_technical_domain_expertise_usage = 4 * (
            math.pow(self.technical_domain_knowledge_score, 2)
        )
        weighted_algorithms_usage = 3 * math.pow(
            self.project_specific_knowledge_score, 2
        )
        weighted_computation_usage = 2 * math.pow(self.cognitive_complexity_score, 2)
        weighted_project_specific_knowledge_usage = 1 * math.pow(
            self.readability_score, 2
        )

        sq_mean = (
            sum(
                [
                    weighted_advanced_programming_techniques_usage,
                    weighted_technical_domain_expertise_usage,
                    weighted_algorithms_usage,
                    weighted_computation_usage,
                    weighted_project_specific_knowledge_usage,
                ]
            )
            / 15
        )

        sum_weighted_sq_complexity_score = (
            weighted_advanced_programming_techniques_usage
            + weighted_technical_domain_expertise_usage
            + weighted_algorithms_usage
            + weighted_computation_usage
            + weighted_project_specific_knowledge_usage
        )
        sum_weighted_sq_complexity_score_mean_correction = (
            sum_weighted_sq_complexity_score * (linear_mean / sq_mean)
        )
        normalized_mean_correction_sum_weighted_sq_complexity_score = (
            sum_weighted_sq_complexity_score_mean_correction / 15
        )

        return normalized_mean_correction_sum_weighted_sq_complexity_score

    def a_score_per_line(self) -> float:
        if self.is_setup_of_declaration:
            return 0
        line_count = self.line_count()
        _normalized_mean_correction_sum_weighted_sq_complexity_score = (
            self._normalized_mean_correction_sum_weighted_sq_complexity_score()
        )
        line_complexity_coefficient = (line_count / 10) ** (1 / 4)
        _normalized_mean_correction_sum_weighted_sq_complexity_score_with_line_complexity = (
            _normalized_mean_correction_sum_weighted_sq_complexity_score
            * line_complexity_coefficient
        )

        a_score = SCORE_MIN_VALUE + SCORE_RANGE_VALUE * math.tanh(
            _normalized_mean_correction_sum_weighted_sq_complexity_score_with_line_complexity
        )
        a_score_pre_line = a_score * line_count

        return a_score_pre_line

    def __str__(self) -> str:
        return f"FunctionAScoreEvaluation: {self.function_name} - {self.a_score_per_line()} -  lines {self.start_line_number}-{self.end_line_number}"


class FileAScoreEvaluation(BaseModel):
    function_complexities: List[FunctionAScoreEvaluation] = Field(
        description="List of function complexity evaluations"
    )

    number_of_functions: int = Field(
        description="Number of functions or methods in the file"
    )

    def __str__(self) -> str:
        return "\n".join(str(f) for f in self.function_complexity)


file_a_score_parser = PydanticOutputParser(pydantic_object=FileAScoreEvaluation)
