from pydantic import AnyHttpUrl

from pangloss_core.settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "{{ cookiecutter.folder_name }}"
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []

    DB_URL: str = "bolt://localhost:7687"
    DB_USER: str = "neo4j"
    DB_PASSWORD: str = "password"
    DB_DATABASE_NAME: str = "neo4j"

    INSTALLED_APPS: list[str] = ["pangloss_core"]


settings = Settings()
