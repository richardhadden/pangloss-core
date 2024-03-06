from __future__ import annotations

import asyncio
import datetime
import functools

import uuid
from typing import (
    Awaitable,
    Callable,
    Concatenate,
)


import neo4j

from pangloss_core.settings import SETTINGS


uri = SETTINGS.DB_URL  # "bolt://localhost:7687"
auth = (SETTINGS.DB_USER, SETTINGS.DB_PASSWORD)
# auth = ("neo4j", "password")
database = SETTINGS.DB_DATABASE_NAME
# database = "neo4j"


# Define a transaction type, for short
Transaction = neo4j.AsyncManagedTransaction


class Application:
    """Experiment: keep driver open for lifetime of app... good idea, but also, find way to use with tests"""

    def __init__(self, uri, user, password):
        self.driver = neo4j.AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self.driver.close()


application = Application(uri=uri, user=auth[0], password=auth[1])


def read_transaction[ModelType, ReturnType, **Params](
    func: Callable[
        Concatenate[ModelType, neo4j.AsyncManagedTransaction, Params],
        Awaitable[ReturnType],
    ],
) -> Callable[Concatenate[ModelType, Params], Awaitable[ReturnType]]:
    async def wrapper(
        cls: ModelType, *args: Params.args, **kwargs: Params.kwargs
    ) -> ReturnType:
        async with neo4j.AsyncGraphDatabase.driver(uri, auth=auth) as driver:
            async with driver.session(database=database) as session:
                bound_func = functools.partial(func, cls)
                records = await session.execute_read(bound_func, *args, **kwargs)
                return records

    return wrapper


def write_transaction[ModelType, ReturnType, **Params](
    func: Callable[
        Concatenate[ModelType, neo4j.AsyncManagedTransaction, Params],
        Awaitable[ReturnType],
    ],
) -> Callable[Concatenate[ModelType, Params], Awaitable[ReturnType]]:
    async def wrapper(
        cls: ModelType, *args: Params.args, **kwargs: Params.kwargs
    ) -> ReturnType:
        async with neo4j.AsyncGraphDatabase.driver(uri, auth=auth) as driver:
            async with driver.session(database=database) as session:
                bound_func = functools.partial(func, cls)
                records = await session.execute_write(bound_func, *args, **kwargs)

                return records

    return wrapper


class Database:
    @classmethod
    @read_transaction
    async def get(
        cls,
        tx: Transaction,
        uid: uuid.UUID,
    ) -> neo4j.Record | None:
        result = await tx.run("MATCH (n {uid: $uid}) RETURN n", uid=str(uid))
        item = await result.single()
        summary = await result.consume()
        print(item)
        print(summary)
        return item

    @write_transaction
    async def write(self, tx: Transaction):
        result = await tx.run(
            "CREATE (new_person:Person {uid: $uid}) RETURN new_person",
            uid=str(test_uid),
        )
        records = await result.values()

        print(records)
        return

    @classmethod
    @write_transaction
    async def dangerously_clear_database(cls, tx: Transaction) -> None:
        result = await tx.run("MATCH (n) DETACH DELETE n")
        summary = await result.consume()


async def api_call():
    # d = Database()
    # await d.write()
    # d = Database()
    # await Database.get(uid=uuid.UUID("a19c71f4-a844-458d-82eb-527307f89aab"))
    await Database.dangerously_clear_database()


if __name__ == "__main__":
    # asyncio.run(main())
    import datetime

    start = datetime.datetime.now()
    asyncio.run(api_call())
    time = datetime.datetime.now() - start
    print(time)
