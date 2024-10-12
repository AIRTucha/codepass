improvement_suggestion_b_score_prompt = """
Analyze the provided code and suggest way to reduce the number of abstraction layers in each function by splitting them into smaller, more specialized functions. 
Focus on reducing visible complexity by delegating specific behaviors to helper functions. 

Use the following abstraction layers:

- System-level abstractions (design patterns, framework-specific logic)
- Application-level abstractions (business logic, service orchestration)
- Component-level abstractions (utility functions, helpers)
- Function-level abstractions (small, reusable operations)
- Low-level operations (basic data manipulations, control flow)
- Recommend which abstraction layers can be hidden behind new functions to make the code simpler and easier to maintain.

Do not consider logging to be an abstraction layer.
Provide only one the most important suggestion. Skip introduction and motivation behind you suggestion, keep it short and focus on explaining the action. 2 sentence maximum.

{error_recovery_instructions}

Code to evaluate: 

{code}
"""
