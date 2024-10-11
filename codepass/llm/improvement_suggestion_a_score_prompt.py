improvement_suggestion_a_score_prompt = """
Analyze the given code and provide suggestions to reduce its cognitive complexity. 

Prioritize factors of cognitive complexity in the following order:

1. Advanced coding techniques (like functional programming paradigms) that are not essential for solving the task but reflect the developer’s preference.
2. Deep technical domain knowledge required, such as advanced algorithms, parallel programming, signal processing, or low-level optimizations.
3. Project-specific knowledge is required, such as the use of third-party libraries or specific business rules
4. Control structures and expressions
5. Readable the code is based on factors like naming conventions, formatting, and non-runtime characteristics

Give just one concise and actionable suggestion. 2 sentence maximum per suggestion.

{error_recovery_instructions}

Code to evaluate: 

{code}
"""
