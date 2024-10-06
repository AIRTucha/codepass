
from dataclasses import dataclass
import time
from threading import Lock
from typing import List

@dataclass
class TokenUsage:
    count: int
    timestamp: float

def estimate_token_count(text: str) -> int:
    # apparently it is a good upper bound estimation
    # for token count for code snippets
    return len(text)

def estimated_push_back_seconds(
        token_count: int,
        token_budget: int,
        tokens_used: List[TokenUsage],
) -> int: 
    current_time = time.time()
    last_item_timestamp_threshold = current_time - 60
    last_minute_used_tokens = [token.count for token in tokens_used if token.timestamp > last_item_timestamp_threshold]
    last_minute_used_tokens_sum = sum(last_minute_used_tokens)

    tokens_left = token_budget - last_minute_used_tokens_sum - token_count

    if tokens_left > 0:
        return 0
    else:
        tokens_removed = 0

        for token in tokens_used:
            tokens_removed += token.count
            if tokens_removed >= tokens_left:
                return token.timestamp - last_item_timestamp_threshold

        return 60
    
class TokenBudgetEstimator:
    tokens_used: List[TokenUsage] = []
    mutex = Lock()

    def __init__(self, token_budget: int):
        self.token_budget = token_budget

    def reserveBudget(self, text: str) -> int:
        with self.mutex:
            current_time = time.time()

            last_minute_used_tokens = [token for token in self.tokens_used if token.timestamp > current_time - 60]
            last_minute_used_tokens_sum = sum([token.count for token in last_minute_used_tokens])
            token_count = estimate_token_count(text)

            print("Token count", token_count, last_minute_used_tokens_sum, len(self.tokens_used))
            if last_minute_used_tokens_sum + token_count < self.token_budget:

                self.tokens_used.append(TokenUsage(token_count, current_time))
                return 0
        
            push_back_seconds = estimated_push_back_seconds(
                token_count, 
                self.token_budget, 
                last_minute_used_tokens,
            )
            print("Push back seconds", push_back_seconds)
            if push_back_seconds > 0:
                return push_back_seconds
            else:

                self.tokens_used.append(TokenUsage(token_count, current_time))
                return 0