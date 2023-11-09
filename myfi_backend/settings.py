import enum
import os
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from pydantic import BaseSettings
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = os.getenv("MYFI_BACKEND_DB_HOST", default="myfi_backend-db")
    db_port: int = int(os.getenv("MYFI_BACKEND_DB_PORT", default="5432"))
    db_user: str = os.getenv("MYFI_BACKEND_DB_USER", default="myfi_backend")
    db_pass: str = os.getenv("MYFI_BACKEND_DB_PASS", default="myfi_backend")
    db_base: str = os.getenv("MYFI_BACKEND_DB_BASE", default="myfi_backend")
    db_echo: bool = False

    # Variables for Redis
    redis_host: str = os.getenv("MYFI_BACKEND_REDIS_HOST", default="myfi_backend-redis")
    redis_port: int = int(os.getenv("MYFI_BACKEND_REDIS_PORT", default="6379"))
    redis_user: Optional[str] = os.getenv("MYFI_BACKEND_REDIS_USER", default=None)
    redis_pass: Optional[str] = os.getenv("MYFI_BACKEND_REDIS_PASS", default=None)
    redis_base: Optional[str] = os.getenv("MYFI_BACKEND_REDIS_BASE", default=None)
    celery_backend = os.getenv(
        "MYFI_BACKEND_CELERY_RESULT_BACKEND",
        default="redis://myfi_backend-redis:6379/0",
    )
    celery_broker = os.getenv(
        "MYFI_BACKEND_CELERY_BROKER_URL",
        default="redis://myfi_backend-redis:6379/0",
    )

    # This variable is used to define
    # multiproc_dir. It's required for [uvi|guni]corn projects.
    prometheus_dir: Path = TEMP_DIR / "prom"

    # Sentry's configuration.
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = 1.0

    # Grpc endpoint for opentelemetry.
    # E.G. http://localhost:4317
    opentelemetry_endpoint: Optional[str] = None

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    class Config:
        env_file = ".env"
        env_prefix = "MYFI_BACKEND_"
        env_file_encoding = "utf-8"


settings = Settings()
