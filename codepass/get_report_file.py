from json import loads
from codepass.file_report import FileReport
from codepass.read_code_files import CodeFile
from typing import Dict, List


def load_report_file() -> dict:
    try:
        with open("codepass.report.json") as f:
            return loads(f.read())
    except FileNotFoundError:
        return {}


def get_report_files(code_files: List[CodeFile]) -> Dict[str, FileReport]:
    file_names = set(file.path for file in code_files)
    report_file = load_report_file()
    return {
        file.get("file_path", ""): FileReport.load_from_dict(file)
        for file in report_file.get("files", [])
        if file.get("file_path", "") in file_names
    }
