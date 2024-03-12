import pytest
import asyncio

from pangloss_core.settings import BaseSettings

from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "MyTestApp"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    DB_URL: str = "bolt://localhost:7687"
    DB_USER: str = "neo4j"
    DB_PASSWORD: str = "password"
    DB_DATABASE_NAME: str = "neo4j"

    INSTALLED_APPS: list[str] = ["pangloss_core"]


settings = Settings()


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    from pangloss_core.database import close_database_connection

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    close_database_connection()
    loop.close()
