from langchain.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field
from typing import List

from pydantic import BaseModel, Field


from pydantic import BaseModel, Field


class FunctionBScoreEvaluation(BaseModel):
    function_name: str = Field(description="Name of the function")

    low_level_implementation_impact: float = Field(
        description="Estimate the impact of low-level technical operations such as memory management, bit manipulation, or hardware-level optimizations on function behavior.\n\
        Score ranges:\n\
        0 - 0.3: Minimal impact from low-level details. These operations are either absent or play a very minor role in function logic.\n\
        0.3 - 0.7: Moderate influence from low-level operations, though still secondary to higher-level logic.\n\
        0.7 - 1: Strong presence of low-level technical operations, which significantly drive the function's behavior."
    )

    technical_domain_logic_impact: float = Field(
        description="Estimate the impact of technical domain knowledge (e.g., algorithms, complex data structures) on function behavior.\n\
        Score ranges:\n\
        0 - 0.3: Function does not depend on technical domain-specific logic or algorithms.\n\
        0.3 - 0.7: Function moderately uses technical domain-specific logic, such as common algorithms or data structures.\n\
        0.7 - 1: Function heavily relies on complex algorithms or technical domain knowledge, which significantly affects its logic."
    )

    business_logic_impact: float = Field(
        description="Estimate the impact of core business logic (high-level decisions and workflows) on function behavior.\n\
        Score ranges:\n\
        0 - 0.3: Minimal impact from business logic. The function is more concerned with technical or low-level operations.\n\
        0.3 - 0.7: Business logic has moderate influence on the function, guiding its structure but not overwhelming other concerns.\n\
        0.7 - 1: Business logic is central to the function’s behavior, driving the core of its design and flow."
    )

    project_specific_knowledge_impact: float = Field(
        description="Estimate the impact of project-specific knowledge, such as third-party libraries or custom framework configurations, on function behavior.\n\
        Score ranges:\n\
        0 - 0.3: Project-specific elements have little impact on the function's behavior.\n\
        0.3 - 0.7: Project-specific knowledge moderately influences function behavior, but other factors also play a major role.\n\
        0.7 - 1: The function is tightly coupled to project-specific libraries or frameworks, and this significantly shapes its behavior."
    )

    external_component_interfacing_impact: float = Field(
        description="Estimate the impact of abstraction layers used for interfacing with external systems like APIs, services, or databases on function behavior.\n\
        Score ranges:\n\
        0 - 0.3: External component interactions are minimal or abstracted away, not playing a significant role.\n\
        0.3 - 0.7: External system interaction has a moderate role in the function, but the function performs other important logic as well.\n\
        0.7 - 1: External component interactions are central to the function, heavily affecting its structure and behavior."
    )

    score_estimation_description: str = Field(
        description="Short description of selected score estimations"
    )

    start_line_number: int = Field(
        description="Number of the first line of the function, considering existing formatting"
    )
    end_line_number: int = Field(
        description="Number of the last line of the function, considering existing formatting"
    )

    def line_count(self) -> int:
        return self.end_line_number - self.start_line_number

    def b_score_per_line(self) -> float:
        layer_impacts = [
            self.low_level_implementation_impact,
            self.technical_domain_logic_impact,
            self.business_logic_impact,
            self.project_specific_knowledge_impact,
            self.external_component_interfacing_impact,
        ]
        high_layer_impacts = [layer for layer in layer_impacts if layer > 0.5]
        return sum(high_layer_impacts) * self.line_count()

    def __str__(self) -> str:
        return f"FunctionBScoreEvaluation: {self.function_name} - {self.b_score_per_line()} lines {self.start_line_number}-{self.end_line_number}"


class FileBScoreEvaluation(BaseModel):
    function_abstraction_level_evaluations: List[FunctionBScoreEvaluation] = Field(
        description="List of function abstraction level evaluations"
    )
    number_of_functions: int = Field(
        description="Number of functions or methods in the file"
    )

    def __str__(self) -> str:
        return "\n".join(str(f) for f in self.function_complexity)


file_b_score_parser = PydanticOutputParser(pydantic_object=FileBScoreEvaluation)
