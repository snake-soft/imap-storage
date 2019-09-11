"""File class"""
from mimetypes import MimeTypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email import encoders
from os.path import getmtime
from datetime import datetime
from builtins import staticmethod

__all__ = ['file_from_local', 'File']


def file_from_local(path):
    """create File object from local path
    :param path: Of the local file
    """
    from os import sep
    with open(path, 'rb') as file:
        data = file.read()
    mime = MimeTypes().guess_type(path)[0]
    name = path.split(sep)[-1]
    time = getmtime(path)
    return File(name, data, mime, time=time)


class File():
    '''Attachment class
    Maybe the following type later:
    from django.core.files import File
    :param filename: Filename as string
    :param data: Data as string
    '''
    def __init__(self, name, data=None, mime=None, time=None, size=None, id_=None):
        self.name = name
        self.data = data
        self.mime = mime
        self.time = time or datetime.now().timestamp()
        self.size = size or len(data)
        self.id_ = id_

    def read(self):
        """Read the data of the object"""
        return self.data

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

    def as_response(self):
        from django.http.response import HttpResponse
        response = HttpResponse(self.read())
        response['Content-Type'] = self.mime
        response['Content-Disposition'] = \
            f'attachment;filename="{self.name}"'
        return response

    def __str__(self):
        return f'{self.name} ({self.hsize})'
