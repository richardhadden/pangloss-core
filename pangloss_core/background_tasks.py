from typing import (
    Callable,
    Awaitable,
    Optional,
    Union,
    overload,
    Any,
    TypeVar,
    ParamSpec,
    TypedDict,
)
from functools import partial, wraps
import asyncio


class BackgroundTastRegistryItem(TypedDict):
    name: str
    function: Callable[[], Awaitable[None]]
    run_in_dev: bool


BackgroundTaskRegistry: list[BackgroundTastRegistryItem] = []


P = ParamSpec("P")  # requires python >= 3.10
R = TypeVar("R")


@overload
def background_task(
    func: Callable[[], Awaitable[None]]
) -> Callable[[], Awaitable[None]]: ...


@overload
def background_task(
    *, run_in_dev: bool = False
) -> Callable[[Callable[[], Awaitable[None]]], Callable[[], Awaitable[None]]]: ...


def background_task(
    func: Optional[Callable[[], Awaitable[None]]] = None, *, run_in_dev: bool = False
) -> Union[
    Callable[[Callable[[], Awaitable[None]]], Callable[[], Awaitable[None]]],
    Callable[[], Awaitable[None]],
]:
    """
    Registers an asynchronous task to be run in the background
    """

    # Without arguments `func` is passed directly to the decorator
    if func is not None:
        if not callable(func):
            raise TypeError("Not a callable. Did you use a non-keyword argument?")
        BackgroundTaskRegistry.append(
            {
                "name": func.__name__,
                "function": wraps(func)(func),
                "run_in_dev": run_in_dev,
            }
        )
        return wraps(func)(func)

    # With arguments, we need to return a function that accepts the function
    def decorator(func: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        BackgroundTaskRegistry.append(
            {
                "name": func.__name__,
                "function": wraps(func)(func),
                "run_in_dev": run_in_dev,
            }
        )
        return wraps(func)(func)

    return decorator
