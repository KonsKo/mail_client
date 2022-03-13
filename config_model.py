"""
Config module.

Module describe structure of application config.
"""

from pydantic import BaseModel
from typing import Optional


class SMTPConfig(BaseModel):
    """SMTP config."""

    host: str
    port: Optional[int] = 25
    domain: str = ''  # e.g. `@google.com`


class WebAppConfig(BaseModel):
    """Server config structure."""

    host: str
    port: int = 8080


class LoggerConfig(BaseModel):
    """Logger config structure."""

    path: str
    level: str = 'DEBUG'


class PostgresConfig(BaseModel):
    """Class for queue config fields determination."""

    user: str
    password: str
    database: str
    hostname: str
    port: str = '5432'


class MainConfig(BaseModel):
    """Application config structure."""

    app: WebAppConfig
    logger: LoggerConfig
    db: PostgresConfig
    smtp: SMTPConfig
