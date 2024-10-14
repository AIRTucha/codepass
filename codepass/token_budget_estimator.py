from dataclasses import dataclass
import time
from threading import Lock
from typing import List

from codepass.read_code_files import CodeFile


@dataclass
class TokenUsage:
    count: int
    timestamp: float


def estimate_remaining_budget(
    token_count: int,
    token_budget: int,
    tokens_used: List[TokenUsage],
) -> int:
    current_time = time.time()
    last_item_timestamp_threshold = current_time - 60
    last_minute_used_tokens = [
        token.count
        for token in tokens_used
        if token.timestamp > last_item_timestamp_threshold
    ]
    last_minute_used_tokens_sum = sum(last_minute_used_tokens)

    return token_budget - last_minute_used_tokens_sum - token_count


def estimated_push_back_seconds(
    token_count: int,
    token_budget: int,
    tokens_used: List[TokenUsage],
) -> int:
    remaining_token_budget = estimate_remaining_budget(
        token_count, token_budget, tokens_used
    )

    if remaining_token_budget > 0:
        return 0
    else:
        current_time = time.time()
        last_item_timestamp_threshold = current_time - 60
        tokens_removed = 0

        for token in tokens_used:
            tokens_removed += token.count
            if tokens_removed >= remaining_token_budget:
                return token.timestamp - last_item_timestamp_threshold

        return 60


class TokenBudgetEstimator:
    tokens_used: List[TokenUsage] = []
    mutex = Lock()

    def __init__(self, token_budget: int):
        self.token_budget = token_budget

    def _remove_old_tokens(self):
        current_time = time.time()
        last_item_timestamp_threshold = current_time - 60
        self.tokens_used = [
            token
            for token in self.tokens_used
            if token.timestamp > last_item_timestamp_threshold
        ]

    def push_external_costs(self, token_count):
        with self.mutex:
            current_time = time.time()
            self.tokens_used.append(TokenUsage(token_count, current_time))

    def reserveBudget(self, code: CodeFile) -> int:
        with self.mutex:
            self._remove_old_tokens()
            last_minute_used_tokens = self.tokens_used

            push_back_seconds = estimated_push_back_seconds(
                code.token_count,
                self.token_budget,
                last_minute_used_tokens,
            )

            if push_back_seconds == 0:
                current_time = time.time()
                self.tokens_used.append(TokenUsage(code.token_count, current_time))
                return 0

            return push_back_seconds

    def await_budget(self, code: CodeFile) -> None:
        while True:
            delay = self.reserveBudget(code)

            if delay > 0:
                time.sleep(float(delay))
            else:
                break

    def has_tasks_in_progress(self) -> bool:
        with self.mutex:
            self._remove_old_tokens()
            return len(self.tokens_used) > 0
