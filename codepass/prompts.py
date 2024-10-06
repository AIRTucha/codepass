file_complexity_evaluation_prompt = """
Please, evaluate every function in the file to estimate cognitive complexity of the code.

Major factors increasing complexity:

- Deeply nested control structures
- Complex algorithms
- Low-level optimization
- Usage of functional programming techniques
- Usage of complex third-party libraries
- Domain specific knowledge
- Advanced coding techniques
- Complicated logic
- Complicated expressions
- Mutable state

Minor factors increasing complexity:

- Complex control structures
- Unnecessary long classes which can be split into smaller ones
- Unnecessary long functions which can be split into smaller ones
- Inheritance
- Parallelism
- Recursion
- Global variables
- Magic numbers
- Long lists of parameters
- Complex networking
- Non-standard coding conventions
- Non-standard naming conventions
- Usage of advanced language features
- Short names
- Unclear names
- Inconsistent names

Pay attention to major factors.

{format_instructions}

Keep in mind JSON does not support comments.

Code: 

{code}

"""

file_abstraction_levels_detection = """
Please, evaluate every function in the file to estimate abstraction levels of the code.

Abstraction levels:

- Operating-system operations and machine instructions
- Programming-language structures and tools
- Low-level implementation structures
- Low-level problem-domain terms
- High-level problem-domain terms

{format_instructions}

Keep in mind JSON does not support comments.

Code: 

{code}

"""