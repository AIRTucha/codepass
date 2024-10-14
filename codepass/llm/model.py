from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.utils import convert_to_secret_str
from langchain_core.runnables import RunnableSerializable

from codepass.llm.estimate_a_score_prompt import estimate_a_score_prompt
from codepass.llm.estimate_b_score_prompt import estimate_b_score_prompt

from codepass.llm.a_score_parser import file_a_score_parser
from codepass.llm.b_score_parser import file_b_score_parser

from codepass.llm.improvement_suggestion_parser import improvement_suggestion_parser
from codepass.llm.improvement_suggestion_prompt import (
    improvement_suggestion_prompt,
)
from threading import Lock
from typing import Any

import os


model_access_mutex = Lock()
OPEN_AI_API_KEY_STR = os.getenv("CODEPASS_OPEN_AI_KEY")

if OPEN_AI_API_KEY_STR is None:
    raise ValueError("CODEPASS_OPEN_AI_KEY is not set")

OPEN_AI_API_KEY = convert_to_secret_str(OPEN_AI_API_KEY_STR)
TEMPERATURE = 0.0
TOP_P = 1
SEED = 3415322
MAX_REQUEST_TIMEOUT = 60
models_map = {}


def get_llm_model(model_name: str):
    with model_access_mutex:
        if model_name not in models_map:
            models_map[model_name] = ChatOpenAI(
                model=model_name,
                api_key=OPEN_AI_API_KEY,
                temperature=TEMPERATURE,
                seed=SEED,
                top_p=1,
                timeout=MAX_REQUEST_TIMEOUT,
            )

        return models_map[model_name]


def file_a_score_model(model_name: str) -> RunnableSerializable[dict, Any]:
    llm_model = get_llm_model(model_name)
    return (
        ChatPromptTemplate.from_template(
            estimate_a_score_prompt,
            partial_variables={
                "format_instructions": file_a_score_parser.get_format_instructions()
            },
        )
        | llm_model
        | file_a_score_parser
    )


def file_b_score_model(model_name: str) -> RunnableSerializable[dict, Any]:
    llm_model = get_llm_model(model_name)
    return (
        ChatPromptTemplate.from_template(
            estimate_b_score_prompt,
            partial_variables={
                "format_instructions": file_b_score_parser.get_format_instructions()
            },
        )
        | llm_model
        | file_b_score_parser
    )


def improvement_suggestion_model(model_name: str) -> RunnableSerializable[dict, Any]:
    llm_model = get_llm_model(model_name)
    return (
        ChatPromptTemplate.from_template(
            improvement_suggestion_prompt,
            partial_variables={
                "format_instructions": improvement_suggestion_parser.get_format_instructions()
            },
        )
        | llm_model
        | improvement_suggestion_parser
    )
