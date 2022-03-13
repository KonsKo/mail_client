"""Module describe structure of emailing."""

from pydantic import BaseModel
from typing import Optional


class SMTPConfig(BaseModel):
    """SMTP config."""

    host: str = '10.1.38.34'
    port: Optional[int] = 25


class Email(BaseModel):
    """Email instance data structure."""

    body: str
    sender: str
    to: str
    subject: Optional[str]
    cc: Optional[str]
    bcc: Optional[str]
    reply_to: Optional[str]  # message id to reply (will be added to chain)

