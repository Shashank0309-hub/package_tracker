from typing import List

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

config = Config(".env")

VERSION = "1.0.0"
SERVICE_NAME: str = config("SERVICE_NAME", cast=str, default="Package Tracker")
DEBUG: bool = config("DEBUG", cast=bool, default=False)
OPENAPI_PREFIX: str = config("OPENAPI_PREFIX", default=None)
ALLOWED_HOSTS: List[str] = config(
        "ALLOWED_HOSTS", cast=CommaSeparatedStrings, default=["*"]
    )
DAYS_FOR_DELETION: int = config("DAYS_FOR_DELETION", cast=int, default=7)


class MySQLEnv:
    HOST: str = config("SQL_HOST", cast=str, default="localhost")
    USER: str = config("SQL_USER", cast=str, default="root")
    PASSWORD: str = config("SQL_PASSWORD", cast=str, default="root")
    DATABASE: str = config("SQL_DATABASE", cast=str, default=None)
