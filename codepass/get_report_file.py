from json import loads
from codepass.file_report import FileReport
from codepass.read_code_files import CodeFile
from typing import Dict, List

from dataclasses import dataclass


def load_report_file() -> dict:
    try:
        with open("codepass.report.json") as f:
            return loads(f.read())
    except FileNotFoundError:
        return {}


@dataclass
class PrevReport:
    a_score: float | None
    b_score: float | None
    files: Dict[str, FileReport]


def get_report_files(code_files: List[CodeFile]) -> PrevReport:
    file_names = set(file.path for file in code_files)
    report_file = load_report_file()
    file = {
        file.get("file_path", ""): FileReport.load_from_dict(file)
        for file in report_file.get("files", [])
        if file.get("file_path", "") in file_names
    }

    return PrevReport(
        a_score=report_file.get("a_score", None),
        b_score=report_file.get("b_score", None),
        files=file,
    )
