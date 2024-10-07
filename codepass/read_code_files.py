from typing import List
from dataclasses import dataclass
import hashlib


def add_line_numbers(code: str) -> str:
    return "\n".join(
        [f"{index+1} {line}" for [index, line] in enumerate(code.split("\n"))]
    )


def estimate_token_count(text: str) -> int:
    # apparently it is a good upper bound estimation
    # for token count for code snippets
    return len(text)


@dataclass
class CodeFile:
    path: str
    code: str
    token_count: int
    hash: str


def read_files(file_paths: List[str], ignore_files: List[str]) -> List[CodeFile]:
    ignore_set = set(ignore_files)

    file_contents = []
    for file_path in file_paths:
        if file_path in ignore_set:
            continue

        with open(file_path) as f:
            file_code = f.read()

            if len(file_code) == 0:
                continue

            code_with_line_numbers = add_line_numbers(file_code)
            file_contents.append(
                CodeFile(
                    path=file_path,
                    code=code_with_line_numbers,
                    hash=hashlib.md5(file_code.encode()).hexdigest(),
                    token_count=estimate_token_count(file_code),
                )
            )

    return file_contents
