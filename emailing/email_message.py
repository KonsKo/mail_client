"""Module for implement message instance."""
import email
import logging
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from email.header import Header
from typing import Optional, Sequence

from emailing.emailing_model import Email

logger = logging.getLogger(__name__)


IMAGE_EXT = (
    'apng', 'avif', 'gif', 'jpeg', 'jpg', 'png', 'svg', 'bmp', 'ico', 'tiff',
)

AUDIO_EXT = (
    'm4a', 'flac', 'mp3',
)


def get_mime_obj(filename: str):  # TODO File type processing
    ext = filename.split('.')[-1]
    if ext in IMAGE_EXT:
        return MIMEImage, ext
    elif ext in AUDIO_EXT:
        return MIMEAudio, ext
    return MIMEApplication, 'octet-stream'


class Message(MIMEMultipart):
    """Message class."""

    def __init__(
        self,
        raw_data: dict,
        attachments: Optional[Sequence] = None,
        message_reply: Optional[email.message.Message] = None,
        **kwargs,
    ):
        """
        Init message instance.

        Args:
            raw_data (dict): data for message creating
            attachments (Optional[Sequence]): attachments to letter
            message_reply (Optional[email.message.Message]): message reply
            kwargs: key parameters

        """
        super().__init__(**kwargs)
        self.msg_mapping = Email(**raw_data)
        self.attachments = attachments
        self.message_reply = message_reply
        self.create_message()

    def create_message(self):
        """Create message."""
        self._create_base_message()
        if self.msg_mapping.subject:
            self.add_header(
                'Subject',
                self.msg_mapping.subject,
            )
        if self.msg_mapping.cc:
            self.add_header(
                'CC',
                self.msg_mapping.cc,
            )
        if self.msg_mapping.bcc:
            self.add_header(
                'BCC',
                self.msg_mapping.bcc,
            )
        if self.msg_mapping.body:
            self.attach(
                MIMEText(
                    _text=self.msg_mapping.body,
                    _charset='utf-8',
                ),
            )
        if self.attachments:
            self.add_attachments()
        if self.message_reply:
            self._add_chain()

    def add_attachments(self):
        """Add attachments to letter."""
        for filename in self.attachments:
            try:
                self._add_attachment(filename)
            except Exception as exception:
                logger.exception(
                    'Adding an attachment was failed. {0}'.format(
                        exception,
                    ),
                )

    def _create_base_message(self):
        """Create base message headers."""
        self['Message-ID'] = make_msgid()
        self.add_header(
            'From',
            self.msg_mapping.sender,
        )
        self.add_header(
            'To',
            self.msg_mapping.to,
        )
        self.add_header(
            'Date',
            formatdate(localtime=True),
        )

    def _add_attachment(self, filename: str):  # TODO file processing ??
        """
        Add single attachment to msg.

        Args:
            filename (str): file to be attached

        """
        mime, ext = get_mime_obj(filename)
        with open(filename, 'rb') as attachment:
            part = mime(
                attachment.read(),
                _subtype='{0}'.format(ext),
            )
        part.add_header(
            'Content-Disposition',
            'inline; filename= {0}'.format(filename),
        )
        self.attach(part)

    def _add_chain(self):
        """
        Make message chaining.

        Raises:
            KeyError: if message reply has no id header

        """
        if not self.message_reply['Message-ID']:
            raise KeyError
        self.add_header(
            'In-Reply-To',
            self.message_reply['Message-ID'],
        )
        if self.message_reply['References']:
            refs = ' '.join(
                (
                    self.message_reply['References'],
                    self.message_reply['Message-ID'],
                ),
            )
            self.add_header(
                'References',
                refs,
            )
        else:
            self.add_header(
                'References',
                self.message_reply['Message-ID'],
            )
