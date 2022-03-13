"""SMTP client module."""
import logging
from email.message import Message

import aiosmtplib
from aiosmtplib.response import SMTPResponse

from config_model import SMTPConfig

logger = logging.getLogger(__name__)

SMTP_OK = 220


class SMTPClient(object):
    """SMTP client."""

    def __init__(self, config: SMTPConfig):
        """
        Init client instance.

        Args:
            config (SMTPConfig): SMTP config

        """
        self.smtp = aiosmtplib.SMTP(
            hostname=config.host,
            port=config.port,
        )

    async def connect(self) -> SMTPResponse:
        """
        Set up SMTP connection and return response.

        Returns:
            response (SMTPResponse): response of command

        """
        try:
            response = await self.smtp.connect()
        except Exception as exception_conn:
            logger.exception(
                'Connection to server was failed. {0}'.format(
                    exception_conn,
                ),
            )
            raise ConnectionError
        if response[0] == SMTP_OK:
            logger.info(
                'SMTP started successfully: {0}'.format(
                    response,
                ),
            )
            return response
        else:
            logger.error(
                'SMTP has problem to start: {0}'.format(
                    response,
                ),
            )
            raise ConnectionError

    async def send_msg(self, msg: Message):
        """
        Send email message.

        Args:
            msg (Message): email message
        """
        try:
            return await self.smtp.send_message(
                message=msg,
            )
        except Exception as exception:
            logger.exception(
                'Sending message(s) was failed. {0}'.format(
                    exception,
                ),
            )
