"""File class"""
from mimetypes import MimeTypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

__all__ = [
    'file_from_local',
    'file_from_upload',
    'file_from_payload',
    'file_from_xml',
    ]


def file_from_local(path):
    """create File object from local path
    :param path: Of the local file
    """
    from os import sep
    with open(path, 'rb') as file:
        data = file.read()
    file = _File()
    file.name = path.split(sep)[-1]
    file.data = data
    file.mime = MimeTypes().guess_type(path)[0]
    # from os.path import getmtime
    # file.time = getmtime(path)
    return file


def file_from_upload(email_obj, uploaded_file):
    """create File object from Django uploaded file"""
    file = _File()
    file.email = email_obj
    file.name = uploaded_file.name
    file.data = uploaded_file.read()
    file.mime = uploaded_file.content_type.split(';')[0]
    file.size = uploaded_file.size
    return file


def file_from_payload(email_obj, payload):
    """create File object from message payload"""
    file = _File()
    file.email = email_obj
    file.name = payload['Content-Disposition'].split(
        'filename=')[-1].strip('"')
    file.data = payload.get_payload()
    file.mime = payload['Content-Type']
    return file


def file_from_xml(email_obj, xml):
    """create File object from xml structure"""
    file = _File()
    file.email = email_obj
    file.name = xml.attrib['name']
    file.mime = xml.attrib['mime'] if 'mime' in xml.attrib else ''
    file.size = xml.attrib['size']
    file.time = float(xml.attrib['time'])
    file.id_ = xml.attrib['id']
    return file


class _File():
    """Attachment class
    Maybe the following type later:
    from django.core.files import File
    :param filename: Filename as string
    :param data: Data as string
    """
    def __init__(self):
        self.email = None
        #, name, data=None, mime=None, time=None, size=None, id_=None
        self.name = None
        self.mime = None
        self.time = datetime.now().timestamp()
        self.id_ = None
        self._data = None
        self._size = None

    @property
    def data(self):
        """
        :TODO: Get automatically
        """
        return self._data or self.email.file_by_name(self.name)

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def size(self):
        return self._size or len(self.data)

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def htime(self):
        return datetime.fromtimestamp(self.time)

    @property
    def hsize(self):
        '''self.size as human readable string'''
        return self.human_readable_size(self.size)

    @property
    def is_binary(self):
        """Make sure that its really a binary string (not 100%)"""
        return self._binary_check(self.data)

    @property
    def mime_obj(self):
        """This is for adding the File to a Multipart Message
        :returns: self as (hopefully) correct Mime Object
        """
        ctype = self.mime
        if ctype is None:  # No guess could be made
            if self.is_binary:
                ctype = 'application/octet-stream'
            else:
                ctype = 'text/plain'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            try:
                msg = MIMEText(str(self.read(), 'utf-8'), _subtype=subtype)
            except TypeError:
                msg = MIMEText(str(self.read()), _subtype=subtype)
        elif maintype == 'image':
            msg = MIMEImage(self.read(), _subtype=subtype)
        elif maintype == 'audio':
            msg = MIMEAudio(self.read(), _subtype=subtype)
        else:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(self.read())
            encoders.encode_base64(msg)
        msg.add_header(
            'Content-Disposition',
            'attachment',
            filename=self.name
        )
        return msg

    def read(self):
        """Read the data of the object"""
        return self.data

    def as_response(self):
        from django.http.response import HttpResponse
        #import pdb; pdb.set_trace()  # <---------
        response = HttpResponse(self.read())
        response['Content-Type'] = self.mime
        response['Content-Disposition'] = \
            f'attachment;filename="{self.name}"'
        return response

    @staticmethod
    def human_readable_size(num, suffix='B'):
        '''changes the format of num into a human readable format'''
        num = int(num)
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    @staticmethod
    def _binary_check(binary):
        textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(
            range(0x20, 0x100)) - {0x7f})
        return bool(binary.translate(None, textchars))

    def __lt__(self, other):
        return self.name < other.name

    def __str__(self):
        return f'{self.name} ({self.hsize})'
