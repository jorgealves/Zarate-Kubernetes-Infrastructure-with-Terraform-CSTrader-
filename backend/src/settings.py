"""
Defines Settings for Database
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Project Settings
    """

    database_driver: str | None = Field(alias="DATABASE_DRIVER", default=None)
    database_username: str | None = Field(alias="DATABASE_USERNAME", default=None)
    database_password: str | None = Field(alias="DATABASE_PASSWORD", default=None)
    database_host: str | None = Field(alias="DATABASE_HOST", default=None)
    database_port: str | None = Field(alias="DATABASE_PORT", default=None)
    database_name: str | None = Field(alias="DATABASE_NAME", default=None)


settings = Settings()
