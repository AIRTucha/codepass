from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.utils import convert_to_secret_str
import os

from codepass.prompts import (
    file_complexity_evaluation_prompt,
    file_abstraction_levels_detection,
)
from codepass.parsers import file_complexity_parser, file_abstraction_level_parser

open_ai_key = os.getenv("CODEPASS_OPEN_AI_KEY")

if open_ai_key is None:
    raise ValueError("CODEPASS_OPEN_AI_KEY is not set")

llm_model = ChatOpenAI(
    model="gpt-4o-mini", api_key=convert_to_secret_str(open_ai_key), temperature=0
)

file_complexity = (
    ChatPromptTemplate.from_template(
        file_complexity_evaluation_prompt,
        partial_variables={
            "format_instructions": file_complexity_parser.get_format_instructions()
        },
    )
    | llm_model
    | file_complexity_parser
)

file_abstraction_levels = (
    ChatPromptTemplate.from_template(
        file_abstraction_levels_detection,
        partial_variables={
            "format_instructions": file_abstraction_level_parser.get_format_instructions()
        },
    )
    | llm_model
    | file_abstraction_level_parser
)
