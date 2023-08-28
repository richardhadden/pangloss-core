import asyncio
import datetime
import functools
import inspect
import uuid
from typing import Literal

import pydantic
from icecream import ic
from neo4j import AsyncGraphDatabase, AsyncManagedTransaction


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


uri = "bolt://localhost:7688"
auth = ("neo4j", "test")


class ReturnType(pydantic.BaseModel):
    uid: uuid.UUID
    last_dependent_change: datetime.datetime
    real_type: Literal["Person"]
    is_deleted: bool
    name: str

    def __init__(self, **kwargs):
        kwargs["last_dependent_change"] = kwargs["last_dependent_change"].to_native()
        super().__init__(**kwargs)


from typing import (
    Any,
    Awaitable,
    Callable,
    Concatenate,
    Coroutine,
    Generic,
    Optional,
    ParamSpec,
    TypeVar,
)

t = TypeVar("t")
P = ParamSpec("P")
R = TypeVar("R")


def db_transaction(
    func: Callable[Concatenate[AsyncManagedTransaction, P], R]
) -> Callable[P, Awaitable[R]]:
    async def wrapper(*args, **kwargs) -> R:
        async with AsyncGraphDatabase.driver(uri, auth=auth) as driver:
            async with driver.session(database="neo4j") as session:
                records = await session.execute_read(func, *args, **kwargs)  # type: ignore
                t = records
                return t

    return wrapper  # type: ignore


@db_transaction
async def get(tx, n: int, x: str, y: str) -> ReturnType:
    result = await tx.run("MATCH (n) RETURN n", x=x)
    records = await result.values()

    return ReturnType(**records[0][0])


async def api_call():
    res = await get(1, "ar", "se")

    ic(res)
    return res


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(api_call())
