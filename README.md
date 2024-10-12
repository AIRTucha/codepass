# Codepass 

## Overview

The Codepass CLI tool evaluates the maintainability of code and provides recommendations. It generates two main scores:

- **a-score**: A complexity assessment using a Large Language Model (LLM).
- **b-score**: Based on Single Level of Abstraction (SLA) principle popularized.

### A-Score

The a-score leverages an LLM to assess your code's complexity. It considers various factors, with more complex code typically resulting in a higher score. Major contributors to high complexity include complicated algorithms, heavy use of third-party libraries, or advanced coding techniques like functional programming that require deep technical expertise to understand. Complicated business logic that demands specific domain knowledge also adds to the complexity.Issues like deeply nested control structures, long methods, or even inconsistent naming can contribute to a higher complexity rating. 

It's also sensitive to code quality best practices—things like avoiding global variables, reducing recursion, or staying away from "magic numbers." The a-score helps you get a clearer picture of how maintainable or complicated your codebase is from a technical perspective.

The overall score for a project should ideally be below **3** to ensure the code is maintainable and easy to understand. However, some files that involve more advanced or domain-specific logic may range between **3 and 4**. The default threshold for the a-score across the whole project is **3.3**, meaning the codebase should strive to keep its complexity below this level, but you can adjust this based on your team's needs.

### B-Score [BETA]

The b-score evaluates your code’s according to the Single Level of Abstraction (SLA) principle promoted by Uncle Bob’s *Clean Code*. The tool analyzes the abstraction levels in your code and assigns a score based on whether functions are mixing high- and low-level operations.

According to the SLA principle, each function should ideally operate at a single level of abstraction. However, having just one level per function is not always a practical or desirable goal. The **b-score** reflects the average number of abstraction layers per function in your codebase. A good target is to aim for around **2** abstraction layers per function, allowing for some flexibility while maintaining clarity. The default threshold for the b-score is **2.5**, which means if your project’s average abstraction level exceeds this value, refactoring may be necessary to make the code more readable and maintainable.

## CLI Configuration

The CLI uses environment variables and accepts multiple arguments and flags.

```bash
codepass your_code/**/*.c 
```

![main](./assets/example.svg)

### Environment Variable

- `CODEPASS_OPEN_AI_KEY`: Required for OpenAI API requests.

### CLI Arguments and Flags

The CLI follows a specific convention for enabling and disabling boolean flags:
- Use `-f` / `--flag` to enable a flag.
- Use `--no-f` / `--no-flag` to disable the flag.

This applies to all boolean flags in the tool.

```bash
-a, --a-score                           # Enable A score (default: True), disable with --no-a-score
-b, --b-score               # Enable B score (default: False), disable with --no-b-score
-ps, --print-improvement-suggestions    # Enable print of improvement suggestions (default: false), disable with --no-print-improvement-suggestions 
-at, --a-score-threshold                # Set A score threshold (default: 3.3)
-bt, --b-score-threshold                # Set B score threshold (default: 2.5)
-c,  --clear                            # Clear existing reports and re-evaluate all files (default: False)
-d, --details                           # Add details for every function into report file (default: False)
-e, --error-info                        # Add debug error message to report file (default: False)
-i, --improvement-suggestions           # Add improvement suggestion to report file (default: False)
```

### Configuration File

The tool supports a `codepass.config.yaml` file for configuration. It includes the same options as CLI flags and an additional option:

- `ignore_files` - An array of glob patterns to exclude certain files from evaluation.

## Poetry Setup

The project is managed using **Poetry**, a dependency management and packaging tool for Python. Follow these steps to set up and work with the project.

### Installing Dependencies

To install all project dependencies defined in the `pyproject.toml` file, run:

```bash
poetry install
```

This will create a virtual environment and install all the necessary packages, including development dependencies.

### Activating the Virtual Environment

To use the project’s virtual environment created by Poetry, activate it with:

```bash
poetry shell
```

Alternatively, you can run commands within the environment without explicitly activating it:

```bash
poetry run <command>
```

For example, to run the CLI tool:

```bash
poetry run codepass --a-score --b-score --recommendation
```

### Install locally

You can install CLI locally by building with `poetry build` and installing package from a `dist/codepass-[x.y.z].tag.gz` with `pip install dist/codepass-[x.y.x].tar.gz` where `[x.y.z]` - represents version of the package.

### Adding New Dependencies

To add new dependencies to the project, use the following command:

```bash
poetry add <package>
```

For development dependencies, append `--dev`:

```bash
poetry add --dev <package>
```

## Features

- **Configurable thresholds**: You can set thresholds for a/b-scores to fail a CI job based on code quality.
- **Progressive mode**: By default, the tool evaluates only new or changed files. Use the `--clear` flag to clear the report and re-evaluate all files.

## Example Usage

### Terminal Output
```
Analyzing files: 62
Changed files: 62
Token count: 161467
Progress 100% 

A score: 3.53
B score: 2.08
Done: 78.2s

Improvement Suggestions: 

File: astrogpt/handler/llm_reasoning/handle_main_menu.py

Suggestion: Refactor the multiple `if-elif` statements that handle different `selected_action.selected_action` values into a dictionary that maps actions to their corresponding handler functions, which will simplify the control structure and improve readability.

Refactor the `handle_main_menu` function by extracting the action handling logic into a new function, `handle_selected_action`, which takes `selected_action`, `chat`, `user`, and `session` as parameters and returns the corresponding action results. This will reduce the complexity of the main function and encapsulate the specific behaviors related to each action type.

File: astrogpt/handler/llm_reasoning/collect_data.py

Suggestion: Consolidate the repeated calls to `get_language(chat)` and `chat.get_message_text()` by storing their results in variables at the beginning of the `collect_data` function, which will reduce redundancy and improve readability.

File: astrogpt/handler/llm_reasoning/generate_advice.py

Suggestion: Refactor the `try-except` block to handle specific exceptions rather than a generic `Exception`, which will improve readability and reduce cognitive complexity by making the error handling more explicit and understandable.

Refactor the `generate_advice` function by creating a helper function, `prepare_advice_input`, that consolidates the gathering and formatting of user data and previous messages into a single operation, thereby reducing the complexity of the main function and improving readability. This will encapsulate the logic for preparing the input for the advice generation, allowing `generate_advice` to focus on the orchestration of the advice generation process.

File: astrogpt/handler/llm_reasoning/detect_unintended_behavior.py

Suggestion: Refactor the `detect_unintended_behavior` function by creating a helper function, `check_warnings_limit`, to encapsulate the warning count check and exception raising logic. This will reduce the visible complexity of the main function and improve maintainability by isolating the warning limit behavior.

File: astrogpt/handler/text_handler.py

Suggestion: Refactor the `handle_text` function by extracting the user retrieval and creation logic into a separate function, such as `retrieve_or_create_user`, which would encapsulate the session management, user existence check, and welcome message sending. This will reduce the complexity of `handle_text` and improve readability by hiding the details of user management behind a dedicated function.

File: astrogpt/bot_utils/send_reply_to_user.py

Suggestion: Refactor the `send_reply_to_user` function by creating a helper function, `prepare_conversation_data`, that encapsulates the logic for gathering and formatting the user name, messages, actions taken, and user language. This will reduce the visible complexity of the main function and improve maintainability by isolating the data preparation logic.

File: astrogpt/handler/llm_reasoning/select_action.py

Suggestion: Refactor the `select_action` function by creating helper functions for retrieving user details (`get_user_details`), formatting messages (`format_conversation`), and preparing the input for `menu_chain.invoke` (`prepare_menu_input`), which will encapsulate the logic and reduce the visible complexity of the main function. This will streamline the function-level abstractions and make the code easier to maintain.

File: astrogpt/handler/stop_handler.py

Suggestion: Refactor the `stop_handler` function by creating a new helper function, `handle_user_subscription`, that encapsulates the logic for retrieving the user and updating their subscription status. This will reduce the complexity of `stop_handler` by hiding the user retrieval and subscription update operations behind a single function call.

File: astrogpt/bot_utils/send_thinking_message.py

Suggestion: Refactor the `send_thinking_message` function by creating a helper function, `prepare_conversation_data`, that encapsulates the logic for retrieving and formatting the user's previous messages and language, thus reducing the complexity of the main function and improving readability.

File: astrogpt/db_utils/add_daily_forecast.py

Suggestion: Refactor the `add_daily_forecast` function by creating a helper function, `create_daily_forecast`, to encapsulate the creation of the `DailyForecast` instance and another helper function, `commit_forecast`, to handle the session operations. This will reduce the complexity of the main function by hiding the component-level and function-level abstractions behind these new specialized functions.

File: astrogpt/db_utils/create_user.py

Suggestion: Refactor the `create_user` function by creating a helper function, `extract_user_info(chat: Chat)`, that encapsulates lines 8-10, which will reduce the visible complexity and separate the user information extraction from the user creation logic. This will simplify the `create_user` function, making it clearer and easier to maintain.

File: astrogpt/db_utils/add_warning.py

Suggestion: Extract the warning creation logic into a separate helper function, `create_warning`, which takes the necessary parameters and returns a new `Warning` instance. This will reduce the complexity of the `add_warning` function by encapsulating the object creation details.

File: astrogpt/db_utils/get_last_advices.py

Suggestion: Create a helper function, `query_user_advices`, to encapsulate the query logic for fetching user advices, which will reduce the complexity in `get_last_advices` by hiding the query details. This will allow `get_last_advices` to focus solely on orchestrating the retrieval of advices.

File: astrogpt/db_utils/add_advice.py

Suggestion: Refactor the `add_advice` function by creating a helper function, `create_advice_instance`, to encapsulate the creation of the `Advice` object, thereby reducing the function-level abstraction and improving readability. This will allow `add_advice` to focus solely on session management and advice persistence.

File: astrogpt/db_utils/add_joke.py

Suggestion: Refactor the `add_joke` function by creating a helper function, `create_joke_instance`, to encapsulate the creation of the `Joke` object, which will reduce the visible complexity and separate the concerns of object instantiation from database operations. This will allow `add_joke` to focus solely on session management and committing the joke.

File: astrogpt/db_utils/get_last_messages.py

Suggestion: Create a helper function, `query_user_messages`, that encapsulates the query logic for retrieving messages based on user ID, and call this function within `get_messages`. This will reduce the complexity of `get_messages` by hiding the query details and focusing it solely on the session and limit parameters.

File: astrogpt/db_utils/remove_user.py

Suggestion: Create a helper function, `execute_delete`, to encapsulate the execution and committing of the delete statement. This will reduce the visible complexity in `remove_user` by hiding the session execution details and focusing on the user removal logic.

A score is too high
```

### Example JSON Report

```json
{
    "file_count": 1,
    "version": "0.2.0",
    "a_score": 2.98,
    "recommendation_count": 0,
    "b_score": 1.0,
    "files": [
        {
            "file_path": "astrogpt/handler/llm_reasoning/collect_data.py",
            "hash": "e62be0853d65c71a2600c8a614566ba4",
            "line_count": 86,
            "a_score": 2.98,
            "b_score": 1.0,
        }
    ]
}
```
