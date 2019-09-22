"""Head class"""
from email.utils import formatdate, parseaddr
from email.mime.multipart import MIMEMultipart
from imap_storage.storage.email.address import Address
from email import message_from_string

__all__ = ['Head']


def new_head(subject, from_addr_obj, to_addr_obj):
    """Create new message and save it
    :param subject: subject as string
    :param from_addr_obj: from-address as *Address* Object
    :param to_addr_obj: to-address as *Address* Object
    :returns: self
    """
    head = Head()
    head['From'] = str(from_addr_obj)
    head['To'] = str(to_addr_obj)
    head['Subject'] = f'{subject}'
    head['Date'] = formatdate(localtime=True)
    return head


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
