from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from yaml import safe_load

from dataclasses import dataclass
from typing import List

from glob import glob

from sys import argv


@dataclass
class CodepassConfig:
    paths: List[str]
    ignore_files: List[str]
    a_score_enabled: bool
    b_score_enabled: bool
    recommendation_enabled: bool
    a_score_threshold: float
    b_score_threshold: float
    clear: bool


def find_ignore_files(ignore_paths: List[str]) -> List[str]:
    ignore_files = []
    for path in ignore_paths:
        ignore_files += glob(path, recursive=True)
    return ignore_files


def load_config_file() -> dict:
    try:
        with open("codepass.config.yaml") as f:
            return safe_load(f)
    except FileNotFoundError:
        return {}


def parser_args(default_config: dict) -> Namespace:
    parser = ArgumentParser(
        description="Analyze code complexity and abstraction levels"
    )

    parser.add_argument(
        "-a",
        "--a-score",
        help="Enable A score",
        type=bool,
        action=BooleanOptionalAction,
        default=default_config.get("a_score_enabled", True),
    )
    parser.add_argument(
        "-b",
        "--b-score",
        help="Enable B score",
        type=bool,
        action=BooleanOptionalAction,
        default=default_config.get("b_score_enabled", True),
    )
    parser.add_argument(
        "-r",
        "--recommendation",
        help="Print recommendations",
        type=bool,
        action=BooleanOptionalAction,
        default=default_config.get("recommendation_enabled", True),
    )
    parser.add_argument(
        "-at",
        "--a-score-threshold",
        help="Threshold for A score",
        type=float,
        default=default_config.get("a_score_threshold", 3.3),
    )
    parser.add_argument(
        "-bt",
        "--b-score-threshold",
        help="Threshold for B score",
        type=float,
        default=default_config.get("b_score_threshold", 2.2),
    )
    parser.add_argument(
        "-c",
        "--clear",
        help="Clear all existing reports",
        type=bool,
        action=BooleanOptionalAction,
        default=False,
    )

    parser.add_argument("paths", nargs="*", type=str)

    return parser.parse_args(argv[1:])


def get_config() -> CodepassConfig:
    config_file = load_config_file()

    args = parser_args(config_file)

    ignore_files = find_ignore_files(config_file.get("ignore_files", []))
    file_paths = args.paths if args.paths else config_file.get("paths", [])

    return CodepassConfig(
        paths=file_paths,
        ignore_files=ignore_files,
        a_score_enabled=args.a_score,
        b_score_enabled=args.b_score,
        recommendation_enabled=args.recommendation,
        a_score_threshold=args.a_score_threshold,
        b_score_threshold=args.b_score_threshold,
        clear=args.clear,
    )
