estimate_a_score_prompt = """
Please evaluate code function by function and identify factors that contributes to the cognitive complexity of each function in the provided code file.
Only consider the factors that are present in the function, ignore complexity of operations hidden in the function calls.

All estimated values should be between 0 and 1.

{format_instructions}

Please note that JSON does not support comments.

{error_recovery_instructions}

Code to evaluate: 

{code}
"""
