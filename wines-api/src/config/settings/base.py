import logging
import pathlib

import decouple
import pydantic
import pydantic_settings


ROOT_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent.parent.parent.parent.resolve()


class BackendBaseSettings(pydantic_settings.BaseSettings):
    TITLE: str = "TuVino"
    VERSION: str = "0.0.1"
    TIMEZONE: str = "UTC-3"
    DESCRIPTION: str | None = None
    DEBUG: bool = False

    SERVER_HOST: str = decouple.config("SERVER_HOST", cast=str)  # type: ignore
    SERVER_PORT: int = decouple.config("SERVER_PORT", cast=int)  # type: ignore
    SERVER_WORKERS: int = decouple.config("SERVER_WORKERS", cast=int)  # type: ignore

    DB_POSTGRES_SCHEMA: str = decouple.config("POSTGRES_SCHEMA", cast=str)  # type: ignore
    DB_POSTGRES_USERNAME: str = decouple.config("POSTGRES_USERNAME", cast=str)  # type: ignore
    DB_POSTGRES_PASSWORD: str = decouple.config("POSTGRES_PASSWORD", cast=str)  # type: ignore
    DB_POSTGRES_HOST: str = decouple.config("POSTGRES_HOST", cast=str)  # type: ignore
    DB_POSTGRES_PORT: str = decouple.config("POSTGRES_PORT", cast=str)  # type: ignore
    DB_POSTGRES_NAME: str = decouple.config("POSTGRES_DB", cast=str)  # type: ignore

    API_PREFIX: str = "/api"
    DOCS_URL: str = "/docs"
    OPENAPI_URL: str = "/openapi.json"
    REDOC_URL: str = "/redoc"
    OPENAPI_PREFIX: str = ""

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8081",
        "http://localhost:8000",
    ]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    IS_ALLOWED_CREDENTIALS: bool = decouple.config("IS_ALLOWED_CREDENTIALS", cast=bool)  # type: ignore
    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    @property
    def DB_POSTGRES_URI(self) -> str:
        return (
            f"{self.DB_POSTGRES_SCHEMA}://"
            f"{self.DB_POSTGRES_USERNAME}:"
            f"{self.DB_POSTGRES_PASSWORD}@"
            f"{self.DB_POSTGRES_HOST}:"
            f"{self.DB_POSTGRES_PORT}/"
            f"{self.DB_POSTGRES_NAME}"
        )

    class Config(pydantic.ConfigDict):
        case_sensitive: bool = True
        env_file: str = f"{str(ROOT_DIR)}/.env"
        validate_assignment: bool = True

    @property
    def set_backend_app_attributes(self) -> dict[str, str | bool | None]:
        """
        Set all `FastAPI` class' attributes with the custom values defined in `BackendBaseSettings`.
        """
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "openapi_url": self.OPENAPI_URL,
            "redoc_url": self.REDOC_URL,
            "openapi_prefix": self.OPENAPI_PREFIX,
            "api_prefix": self.API_PREFIX,
        }
