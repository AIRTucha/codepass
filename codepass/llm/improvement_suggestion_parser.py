from langchain.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field

from pydantic import BaseModel, Field


class ImprovementSuggestion(BaseModel):
    improvement_suggestion: str = Field(
        description="A short suggestion on how to improve the code, do not include details why it is important"
    )

    start_line_number: int = Field(
        description="Number of the first line of the function, considering existing formatting"
    )

    end_line_number: int = Field(
        description="Number of the last line of the function, considering existing formatting"
    )

    def __str__(self) -> str:
        return f"{self.start_line_number}-{self.end_line_number}: {self.improvement_suggestion}"


improvement_suggestion_parser = PydanticOutputParser(
    pydantic_object=ImprovementSuggestion
)
