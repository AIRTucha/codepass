from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.utils import convert_to_secret_str
from langchain_core.output_parsers import StrOutputParser

from codepass.llm.estimate_a_score_prompt import estimate_a_score_prompt
from codepass.llm.estimate_b_score_prompt import estimate_b_score_prompt

from codepass.llm.a_score_parser import file_a_score_parser
from codepass.llm.b_score_parser import file_b_score_parser

from codepass.llm.improvement_suggestion_a_score_prompt import (
    improvement_suggestion_a_score_prompt,
)
from codepass.llm.improvement_suggestion_b_score_prompt import (
    improvement_suggestion_b_score_prompt,
)

import os


open_ai_key = os.getenv("CODEPASS_OPEN_AI_KEY")

if open_ai_key is None:
    raise ValueError("CODEPASS_OPEN_AI_KEY is not set")

llm_model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=convert_to_secret_str(open_ai_key),
    temperature=0.0001,
    seed=8315108,
    top_p=1,
)

file_a_score_model = (
    ChatPromptTemplate.from_template(
        estimate_a_score_prompt,
        partial_variables={
            "format_instructions": file_a_score_parser.get_format_instructions()
        },
    )
    | llm_model
    | file_a_score_parser
)

file_b_score_model = (
    ChatPromptTemplate.from_template(
        estimate_b_score_prompt,
        partial_variables={
            "format_instructions": file_b_score_parser.get_format_instructions()
        },
    )
    | llm_model
    | file_b_score_parser
)

improvement_suggestion_a_score_model = (
    ChatPromptTemplate.from_template(
        improvement_suggestion_a_score_prompt,
    )
    | llm_model
    | StrOutputParser()
)

improvement_suggestion_b_score_model = (
    ChatPromptTemplate.from_template(
        improvement_suggestion_b_score_prompt,
    )
    | llm_model
    | StrOutputParser()
)
