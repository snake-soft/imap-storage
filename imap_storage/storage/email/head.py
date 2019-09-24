"""Head class"""
from email.utils import formatdate, parseaddr
from email.mime.multipart import MIMEMultipart
from email import message_from_string
from .address import Address


class Head(MIMEMultipart):
    """Represents the head of an Email
    :param msg_obj: either pass a msg_obj to parse or run Head().new(*)
    """
    def __init__(self, msg_obj=None):
        super().__init__()
        if msg_obj:
            self._parse(msg_obj)

    def _parse(self, email_obj):
        if isinstance(email_obj, str):
            email_obj = message_from_string(email_obj)
        self['From'] = str(Address(parseaddr(email_obj['From'])))
        self['To'] = str(Address(parseaddr(email_obj['To'])))
        self['Subject'] = email_obj['Subject']
        self['Date'] = formatdate(localtime=True)
