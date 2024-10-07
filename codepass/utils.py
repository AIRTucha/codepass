from typing import TypeVar, Tuple, List, Callable

T = TypeVar("T")


def partition(
    items: List[T], predicate: Callable[[T], bool]
) -> Tuple[List[T], List[T]]:
    good = []
    bad = []

    for item in items:
        if predicate(item):
            good.append(item)
        else:
            bad.append(item)

    return (good, bad)
