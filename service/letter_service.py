"""Letter service module."""
import logging

from service.base_service import BaseService

logger = logging.getLogger(__name__)


class LetterService(BaseService):
    """Letter service."""

    async def send_email(self):  # TODO
        """Get letter from db by id, create email and send it."""
        # smtp = self.app['smtp']
        # letter = await self.retrieve(bake='first')
        # email = Message(raw_data=letter)
        # rr = await smtp.send_msg(msg=email)

        raise NotImplementedError
