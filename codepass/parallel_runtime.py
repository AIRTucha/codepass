import concurrent.futures
import time
import sys
from typing import List
from threading import Thread
from dataclasses import dataclass
from time import sleep
import sys
from threading import Lock


@dataclass
class Task:
    task: callable
    args: List[any]
    budget: int

    def run(self, executor: concurrent.futures.ThreadPoolExecutor):
        return executor.submit(self.task, *self.args)


class ParallelRuntime:
    def __init__(self, token_budget_estimator):
        self._tasks = []
        self._results = []
        self.token_budget_estimator = token_budget_estimator
        self.lock = Lock()
        self.finished_budget = 0

    def _handle_result(self, budget):
        def callback(future):
            with self.lock:
                self.finished_budget += budget
                self._results.append(future.result())

        return callback

    def add_task(self, budget: int, task: callable, *args: List[any]):
        self._tasks.append(Task(task, args, budget))

    def run_tasks(self):
        if len(self._tasks) == 0:
            return []

        futures = []
        animation_thread = self._print_progress()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
            for task in self._tasks:
                future = task.run(executor)
                future.add_done_callback(self._handle_result(task.budget))
                futures.append(future)

        concurrent.futures.wait(futures)
        animation_thread.join()
        return self._results

    def _print_progress(self):
        def animation():
            token_submitted_animation = "|/-\\"
            no_tokens_animation = "..."
            char_index = 0

            while True:
                if char_index == sys.maxsize:
                    char_index = 0
                else:
                    char_index += 1

                result_count = len(self._results)
                task_count = len(self._tasks)

                is_finished = result_count == task_count

                if is_finished:
                    self._print_progress_text("Progress 100%    \n")
                    break

                progress_percentage = (
                    self.finished_budget
                    / sum([task.budget for task in self._tasks])
                    * 100
                )

                progress_text = f"Progress {round(progress_percentage, 1)}%"

                if self.token_budget_estimator.has_tasks_in_progress():
                    progress_text += (
                        " " + token_submitted_animation[char_index % 3] + " "
                    )
                else:
                    point_count = char_index % 4
                    empty_extra_space = 3 - point_count
                    progress_text += (
                        no_tokens_animation[0 : char_index % 4]
                        + " " * empty_extra_space
                    )

                self._print_progress_text(progress_text)

                sleep(0.1)

        animation_thread = Thread(target=animation)
        animation_thread.start()

        return animation_thread

    def _print_progress_text(self, text):
        sys.stdout.write(f"\r{text}")
        sys.stdout.flush()
