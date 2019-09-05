"""Head class"""
from email.utils import formatdate, parseaddr
from email.mime.multipart import MIMEMultipart
from .address import Address

__all__ = ['Head']


class Head(MIMEMultipart):
#class Head:
    """Represents the head of an Email
    :param msg_obj: either pass a msg_obj to parse or run Head().new(*)
    """
    def __init__(self, msg_obj=None):
        super().__init__()
        if msg_obj:
            self._parse(msg_obj)

    def new(self, subject, from_addr_obj, to_addr_obj):
        """Create new message and save it
        :param subject: subject as string
        :param from_addr_obj: from-address as *Address* Object
        :param to_addr_obj: to-address as *Address* Object
        :returns: self
        """
        self['From'] = str(from_addr_obj)
        self['To'] = str(to_addr_obj)
        self['Subject'] = f'{subject}'
        self['Date'] = formatdate(localtime=True)
        return self

    def _parse(self, msg_obj):
        self['From'] = str(Address(parseaddr(msg_obj['From'])))
        self['To'] = str(Address(parseaddr(msg_obj['To'])))
        self['Subject'] = msg_obj['Subject']
        self['Date'] = formatdate(localtime=True)
