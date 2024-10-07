import concurrent.futures
import time
import sys
from typing import List

from dataclasses import dataclass


@dataclass
class Task:
    task: callable
    args: List[any]

    def run(self, executor: concurrent.futures.ThreadPoolExecutor):
        return executor.submit(self.task, *self.args)


class ParallelRuntime:
    _tasks: List[Task] = []

    _results = []

    def _handle_result(self):
        def callback(future):
            self._results.append(future.result())
            self._print_progress()

        return callback

    def add_task(self, task: callable, *args: List[any]):
        self._tasks.append(Task(task, args))

    def run_tasks(self):
        if len(self._tasks) == 0:
            return []

        futures = []
        self._print_progress()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for task in self._tasks:
                future = task.run(executor)
                future.add_done_callback(self._handle_result())
                futures.append(future)

        concurrent.futures.wait(futures)
        self._print_finish()
        return self._results

    def _print_progress(self):
        sys.stdout.write(
            "\rProgress %d%%" % (len(self._results) / len(self._tasks) * 100)
        )
        sys.stdout.flush()

    def _print_finish(self):
        sys.stdout.write("\rProgress 100% \n")
        sys.stdout.flush()
