from __future__ import annotations

import typing

from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class BaseSettings(PydanticBaseSettings):
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl]
    INSTALLED_APPS: list[str]
    DB_URL: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DATABASE_NAME: str

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
        cls, v: typing.Union[str, list[str]]
    ) -> typing.Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, *args, **kwargs):
        # When initialising settings, copy it to this global var for access
        # within pangloss_core
        global SETTINGS
        SETTINGS = self
        
        super().__init__(*args, **kwargs)


SETTINGS: BaseSettings