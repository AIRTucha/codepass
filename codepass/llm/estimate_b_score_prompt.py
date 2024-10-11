estimate_b_score_prompt = """
Please evaluate code function by function and estimate the contribution of each abstraction layer to the overall behavior of the function. 
For each layer, return a score between 0 and 1 indicating the impact of that layer. 

{format_instructions}

Please note that JSON does not support comments.

{error_recovery_instructions}

Code to evaluate: 

{code}
"""
