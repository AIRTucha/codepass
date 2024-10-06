import sys

from codepass.parsers import FileComplexityEvaluation, FileAbstractionEvaluation, FunctionAbstractionLevels, AbstractionLevelPriority
from codepass.model import file_complexity, file_abstraction_levels
from codepass.token_budget_estimator import TokenBudgetEstimator

import asyncio

import glob

from dataclasses import dataclass

from typing import Optional

from json import dumps
from importlib.metadata import version


import time

@dataclass
class ComplexityEvaluationResult:
    file_path: str
    line_count: int
    a_score: int
    improvement_suggestions: str

    error_message: Optional[str] = None

@dataclass
class AbstractionEvaluationResult:
    file_path: str
    line_count: int
    b_score: int
    most_complex_function: str = ""

    error_message: Optional[str] = None


code_improvement_suggestions_threshold = 3.3

token_budget_estimator = TokenBudgetEstimator(200 * 1000)

def evaluate_abstraction_level(levels: FunctionAbstractionLevels) -> int:
    # print('Abstraction levels', levels.function_name, levels.abstraction_levels)
    abstraction_levels_int = set([int(level.abstraction_level) for level in levels.abstraction_levels if level.confidence > 0.75 and level.priority > AbstractionLevelPriority.does_not_affect_core_behavior])
    return len(abstraction_levels_int)


def evaluate_complexity(code: str) -> FileComplexityEvaluation:
    while True:
        delay = token_budget_estimator.reserveBudget(code)

        if delay > 0:
            print(f"Token budget exceeded, waiting {delay} seconds")
            time.sleep(float(delay))
        else:
            break

    return file_complexity.invoke({"code": code})

async def evaluate_file_complexity(file_path: str) -> ComplexityEvaluationResult:
     with open(file_path) as f:
        file_code = f.read()

        print(f"Complexity processing {file_path}")

        if len(file_code) == 0:
            return ComplexityEvaluationResult(
                file_path=file_path,
                line_count=0,
                a_score=0,
                improvement_suggestions="",
            )
        try:
            augmented_code = "\n".join([f'{index+1} {line}' for [index, line] in enumerate(file_code.split("\n"))])
   
            file_evaluation: FileComplexityEvaluation = await asyncio.to_thread(evaluate_complexity, augmented_code)
            print(f"Complexity Evaluated {file_path}")
            number_of_lines = sum([f.end_line_number - f.start_line_number for f in file_evaluation.function_complexities])

            if number_of_lines == 0:
                return ComplexityEvaluationResult(
                    file_path=file_path,
                    line_count=0,
                    a_score=0,
                    improvement_suggestions="",
                )
            complexity_score = sum([int(f.code_complexity_score) * (f.end_line_number - f.start_line_number) for f in file_evaluation.function_complexities])
            a_score = complexity_score / number_of_lines
    
            return ComplexityEvaluationResult(
                line_count=number_of_lines,
                a_score=a_score,
                file_path=file_path,
                improvement_suggestions=file_evaluation.improvement_suggestions if a_score > code_improvement_suggestions_threshold else "",
            )
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return ComplexityEvaluationResult(
                file_path=file_path,
                line_count=0,
                error_message=str(e),
                a_score=0,
                improvement_suggestions=""
            )
        
async def evaluate_abstraction_levels(file_path: str) -> AbstractionEvaluationResult:
     with open(file_path) as f:
        file_code = f.read()

        print(f"Abstraction Levels {file_path}")

        if len(file_code) == 0:
            return AbstractionEvaluationResult(
                file_path=file_path,
                line_count=0,
                b_score=0,
            )
        try:
            augmented_code = "\n".join([f'{index+1} {line}' for [index, line] in enumerate(file_code.split("\n"))])
            while True:
                delay = token_budget_estimator.reserveBudget(file_code)

                if delay > 0:
                    print(f"Token budget exceeded, waiting {delay} seconds")
                    time.sleep(float(delay))
                else:
                    break
            file_abstraction_level_evaluation: FileAbstractionEvaluation = await asyncio.to_thread(file_abstraction_levels.invoke, {"code": augmented_code})
            print(f"Abstraction Evaluated {file_path}")
            number_of_lines = sum([f.end_line_number - f.start_line_number for f in file_abstraction_level_evaluation.function_abstraction_level_evaluation])

            if number_of_lines == 0:
                return AbstractionEvaluationResult(
                    file_path=file_path,
                    line_count=0,
                    b_score=0,
                )
            complexity_score = sum([evaluate_abstraction_level(f) * (f.end_line_number - f.start_line_number) for f in file_abstraction_level_evaluation.function_abstraction_level_evaluation])
            abs_level_est = [ (evaluate_abstraction_level(f), f.function_name) for f in file_abstraction_level_evaluation.function_abstraction_level_evaluation]
            abs_level_est.sort(key=lambda x: x[0], reverse=True)
            most_complex_function = f'{abs_level_est[0][1]} - {abs_level_est[0][0]}' if len(abs_level_est) > 0 else ""
            b_score = complexity_score / number_of_lines

            return AbstractionEvaluationResult(
                line_count=number_of_lines,
                b_score=b_score,
                file_path=file_path,
                most_complex_function=most_complex_function,
            )
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return AbstractionEvaluationResult(
                file_path=file_path,
                line_count=0,
                error_message=str(e),
                a_score=0,
            )

async def main():
    start = time.time()


    

    complexity_tasks = []

    file_count = 0
    for filename in sys.argv[1:]:
        file_count += 1
        complexity_tasks.append(evaluate_file_complexity(filename))

    function_complexity: list[ComplexityEvaluationResult] = []
    complexity_result = await asyncio.gather(*complexity_tasks)

    for file_evaluation in complexity_result:
        function_complexity.append(file_evaluation)


    abstraction_levels_tasks = []


    # for filename in sys.argv[1:]:
    #     abstraction_levels_tasks.append(evaluate_abstraction_levels(filename))

    function_abstraction_levels: list[AbstractionEvaluationResult] = []
    abstraction_levels_result = await asyncio.gather(*abstraction_levels_tasks)

    for file_evaluation in abstraction_levels_result:
        function_abstraction_levels.append(file_evaluation)

    end = time.time()


    print(f"Done " + str(end - start))

    total_lines = sum(f.line_count for f in function_complexity)
    total_a_score = sum(f.a_score * f.line_count for f in function_complexity)
    # total_b_score = sum(f.b_score * f.line_count for f in function_abstraction_levels)
    print()

    with open("codepass.report.json", "w") as f:

        f.write(dumps(
            {
            "file_count": file_count,
            "version": version("codepass"),
            "a_score": total_a_score / total_lines if total_lines > 0 else 0,
            # "b_score": total_b_score / total_lines if total_lines > 0 else 0,
            "recommendation_count": sum(1 for f in function_complexity if f.a_score > code_improvement_suggestions_threshold),
            "files": [
                {
                    "file_path": f.file_path,
                    "line_count": f.line_count,
                    "a_score": f.a_score,
                    # "b_score": function_abstraction_levels[i].b_score,
                    "error_message": f.error_message if f.error_message else "",
                    # "most_complex_function": function_abstraction_levels[i].most_complex_function if function_abstraction_levels[i].b_score > 2 else "",
                    "improvement_suggestions": f.improvement_suggestions,
    
                }
                for [i,f] in enumerate(function_complexity) if f.line_count > 0
            ]
        }, indent=4))

    

