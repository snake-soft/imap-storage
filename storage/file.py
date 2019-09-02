"""File class"""
from mimetypes import MimeTypes
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email import encoders
from os.path import getmtime

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
    def __init__(self, name, data, mime, time=None):
        self.name = name
        self.data = data
        self.time = time
        self.size = len(data)
        self.mime = mime

    def read(self):
        """Read the data of the object"""
        return self.data

    @property
    def hsize(self):
        '''self.size as human readable string'''
        return self.human_readable_size(self.size)

    @property
    def mime_obj(self):
        """This is for adding the File to a Multipart Message
        :returns: self as (hopefully) correct Mime Object
        """
        ctype = self.mime
        if ctype is None:  # No guess could be made
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            msg = MIMEText(str(self.read(), 'utf-8'), _subtype=subtype)
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
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def __str__(self):
        return f'{self.name} ({self.hsize})'
