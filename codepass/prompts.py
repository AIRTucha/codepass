file_complexity_evaluation_prompt = """
Please evaluate the cognitive complexity of each function in the provided code file. Use the following criteria to assess the complexity, focusing on identifying and prioritizing the most impactful issues.

Major factors that significantly increase complexity:

 - Use of advanced algorithms requiring domain-specific knowledge
 - Low-level optimizations
 - Use of complex third-party libraries (e.g., Rx.js, Pandas, TensorFlow)
 - Business logic requiring domain-specific expertise
 - Advanced coding techniques (e.g., functional programming)
 - Complex or anonymous expressions
 - Excessive reliance on mutable state
 - Minor factors that moderately increase complexity:

 - Deeply nested control structures (more than 3 levels)
 - Long classes (over 200 lines)
 - Long functions (over 100 lines)
 - Parallelism and concurrency patterns
 - Recursion
 - Use of global variables
 - Magic numbers (unexplained constants)
 - Long lists of positional parameters
 - Non-standard coding or naming conventions
 - Use of advanced language features (e.g., metaprogramming, reflection, etc.)
 - Short, unclear, or inconsistent names (for variables, functions, or classes)

Complexity Scoring:

 - Focus on identifying the most significant major issues in the code that contribute to higher cognitive load.
 - Provide suggestions for improvement based on the most significant issues identified.

{format_instructions}

Please note that JSON does not support comments.

{error_recovery_instructions}

Code to evaluate: 

{code}
"""

file_abstraction_levels_detection = """Please evaluate each function in the provided code file to estimate the abstraction levels present in the code. Use the following categories to classify the abstraction level for each function or code segment:

Abstraction Levels:

 - Operating-system operations and machine instructions: Code interacting with hardware, system calls, or low-level machine operations.
 - Programming-language structures and tools: Language-specific operations (e.g., arithmetics, comparators, boolean logic, bitwise operations etc.) and usage of language utilities.
 - Low-level implementation structures: Data structures, algorithms, or patterns used for implementation, which are not directly related to the problem domain.
 - Low-level problem-domain terms: Specific terms and concepts from the problem domain, but still close to implementation details.
 - High-level problem-domain terms: Abstracted terms from the problem domain, focusing on business logic or high-level design without going into implementation details.
 - Identify the highest level of abstraction used in each function and suggest any opportunities for improvement in terms of simplifying or refactoring the code to align with appropriate abstraction levels.

{format_instructions}

Please note that JSON does not support comments.

{error_recovery_instructions}

Code to evaluate: 

{code}
"""
