from langchain.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional


class CodeComplexityScore(str, Enum):
    good_production_code = 1
    average_production_code = 2
    domain_knowledge_required = 3
    complex_code = 4
    very_complex_code = 5


code_complexity_score_description = """
Well written highly readable simple code - 1
Average production code that any programmer can understand - 2
Code requiring some specific domain knowledge or advanced techniques e.g. functional programming - 3-4
Extremely complex code due to many criteria- 5
"""


class FunctionComplexityEvaluation(BaseModel):
    function_name: str = Field(description="Name of the function")
    code_complexity_score: CodeComplexityScore = Field(
        description=code_complexity_score_description
    )
    code_complexity_score_description: str = Field(
        description="Short description of the code complexity score"
    )
    start_line_number: int = Field(
        description="Number of the first line of the function, considering existing formatting"
    )
    end_line_number: int = Field(
        description="Number of the last line of the function, considering existing formatting"
    )
    line_count: int = Field(description="Number of lines in the function")

    def count_lines(self) -> int:
        return self.end_line_number - self.start_line_number

    def complexity_score_impact(self) -> int:
        return int(self.code_complexity_score) * self.count_lines()

    def __str__(self) -> str:
        return f"FunctionComplexityEvaluation: {self.function_name} - {self.code_complexity_score} - {self.code_complexity_score_description} lines {self.start_line_number}-{self.end_line_number}"


improvements_suggestions_description = """
Short suggestions improvement for the code: 
    - Focus on the most important issue
    - Explain exactly how to refactor the code with details like names of abstractions involved in the refactoring
    - Do not explanation motivation behind your suggestion
    - 2 sentences max
"""


class FileComplexityEvaluation(BaseModel):
    function_complexities: List[FunctionComplexityEvaluation] = Field(
        description="List of function complexity evaluations"
    )
    improvement_suggestions: Optional[str] = Field(
        description=improvements_suggestions_description
    )
    number_of_functions: int = Field(
        description="Number of functions or methods in the file"
    )

    def __str__(self) -> str:
        return "\n".join(str(f) for f in self.function_complexity)


file_complexity_parser = PydanticOutputParser(pydantic_object=FileComplexityEvaluation)


class AbstractionLevels(str, Enum):
    operation_system_and_machine_instructions = 1
    language_structures_and_tools = 2
    low_level_implementation_structures = 3
    low_level_domain_problem_logic = 4
    high_level_domain_problem_logic = 5


class AbstractionLevelPriority(str, Enum):
    does_not_affect_core_behavior = 1
    minor_affect_core_behavior = 2
    major_affect_core_behavior = 3


class AbstractionLevelEstimation(BaseModel):
    motivation: str = Field(
        description="Short motivation of claim for the abstraction level"
    )

    confidence: float = Field(description="Detection confidence from 0 to 1")

    priority: AbstractionLevelPriority = Field(
        description="Estimate how much abstraction level affects core behavior from 1 to 3"
    )

    abstraction_level: AbstractionLevels = Field(
        description="Abstraction level of the line"
    )

    def __str__(self) -> str:
        return f"AbstractionLevelsWithMotivation: {self.line_number} - {self.abstraction_level}"


class FunctionAbstractionLevels(BaseModel):
    function_name: str = Field(description="Name of the function")
    abstraction_levels: List[AbstractionLevelEstimation] = Field(
        description="List of abstraction levels present in the function"
    )
    start_line_number: int = Field(
        description="Number of the first line of the function, considering existing formatting"
    )
    end_line_number: int = Field(
        description="Number of the last line of the function, considering existing formatting"
    )

    def count_lines(self) -> int:
        return self.end_line_number - self.start_line_number

    def __str__(self) -> str:
        return f"FunctionAbstractionLevels: {self.function_name} - {self.code_complexity_score} - {self.code_complexity_score_description} lines {self.start_line_number}-{self.end_line_number}"


class FileAbstractionEvaluation(BaseModel):
    function_abstraction_level_evaluations: List[FunctionAbstractionLevels] = Field(
        description="List of function abstraction level evaluations"
    )
    number_of_functions: int = Field(
        description="Number of functions or methods in the file"
    )

    def __str__(self) -> str:
        return "\n".join(str(f) for f in self.function_complexity)


file_abstraction_level_parser = PydanticOutputParser(
    pydantic_object=FileAbstractionEvaluation
)
