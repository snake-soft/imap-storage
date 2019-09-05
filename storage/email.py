''' Email and Attachment class '''
from email import message_from_bytes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from copy import deepcopy

from .head import Head
from .address import Address
from .body import Body
from .file import File

__all__ = ['Email']


class Email:
    """Emails as data storage interface
    :param imap: Imap connection
    :param uid: new object if None - make sure to run *new* method
    """
    def __init__(self, imap, uid=None):
        self.imap = imap
        self.uid = uid
        self._head = None
        self._body = None
        self._files = None

    def new(self, directory, from_addr=None, from_displ=None):
        """needs to be runned if its a ne Email with no uid"""
        directory = '%s%s%s' % (
            '/' if directory[0] != '/' else '',
            directory,
            '/' if directory[-1] != '/' else '',
            )
        subject = f'{self.imap.config.tag} {directory}'
        from_addr_obj = Address(
            addr_spec=from_addr or self.imap.config.imap.user,
            display_name=from_displ or self.imap.config.imap.user
            )
        to_addr_obj = Address(
            addr_spec=self.imap.config.imap.user,
            display_name=self.imap.config.imap.user
            )
        self._head = Head().new(subject, from_addr_obj, to_addr_obj)
        self._body = Body().new()
        return self

    @property
    def head(self):
        """access to the head object, fetch if not already done"""
        if not self._head:
            head = self.imap.fetch(
                self.uid, 'BODY[HEADER]')[self.uid][b'BODY[HEADER]']
            self._head = Head(message_from_bytes(head))
        return self._head

    @property
    def body(self):
        """access to the body object, fetch if not already done"""
        if self._body is None:
            body = self.imap.fetch(self.uid, 'BODY[1]')[self.uid][b'BODY[1]']
            self._body = Body(body.decode())  # ET.fromstring(body)
        return self._body

    @property
    def files(self):
        """access to the file objects, fetch if not already done"""
        if self._files is None:
            self._files = []
            if self.uid:
                msg = self.imap.fetch(self.uid, 'RFC822')[self.uid][b'RFC822']
                msg = message_from_bytes(msg)
                import pdb; pdb.set_trace()  # <---------
                for payload in msg.get_payload()[1:]:  # first is body
                    name = payload['Content-Disposition'].split(
                        'filename=')[-1].strip('"')
                    mime = payload['Content-Type']
                    data = payload.get_payload()
                    self._files.append(File(name, data, mime))
        return self._files

    @property
    def plain(self):
        return self.to_string(html=False)
        
    @property
    def html(self):
        return self.to_string(html=True)

    def to_string(self, html=False):
        """ https://stackoverflow.com/a/43157340
        mixed
        |---alternative
        |   |---text
        |   |---related
        |       |---html
        |       |---inline image
        |       |---inline image
        |---attachment
        |---attachment
        """
        msg = self.head
        msg_alt = MIMEMultipart('alternative')
        body = MIMEText(None, 'plain', 'utf-8')
        body.replace_header('content-transfer-encoding', 'quoted-printable')
        body.set_payload(str(self.body), 'utf-8')
        msg_alt.attach(body)

        if html:
            msg_rel = MIMEMultipart('related')
            body_html = MIMEText(None, 'html', 'utf-8')
            body_html.replace_header(
                'content-transfer-encoding', 'quoted-printable')
            body_html.set_payload(str(self.body), 'utf-8')
            msg_rel.attach(body_html)
            msg_alt.attach(msg_rel)

        msg.attach(msg_alt)
        for file in self.files:
            msg.attach(file.mime_obj)
        return str(msg)

    def file_by_name(self, name):
        return [file for file in self.files if file.name == name][0]

    def file_by_id(self, id_):
        for file in self.body.xml_files:
            if file.attrib['id'] == id_:
                return self.file_by_name(file.attrib['name'])

    def add_item(self, tag, text=None, attribs=None, parent=None):
        """forwards to body method"""
        self.body.add_item(tag, text=text, attribs=attribs, parent=parent)

    def remove_item(self, id_):
        """forwards to body method"""
        self.body.remove_item(id_)

    def add_file(self, file_obj):
        """add file to email
        :param file_obj: Object of class storage.file.File
        :returns: success bool
        """
        if file_obj.name not in [file.name for file in self.files]:
            self._files.append(file_obj)
            attribs = {
                'name': file_obj.name,
                'size': file_obj.size,
                }
            if file_obj.time:
                attribs['time'] = file_obj.time
            self.body.add_item('file', attribs=attribs)
            ret = True
        else:
            ret = False
        return ret

    def remove_file_by_attrib(self, attrib, value):
        """remove file from email
        eg. remove_file_by_attrib('id', 'ldsKLfds')
        :param attrib: attribute to select
        :param value: value of the attribute
        """
        for bad in self.body.xml.xpath(f"//*[@{attrib}=\'{value}\']"):
            name = bad.get('name')
            bad.getparent().remove(bad)
        for file in self.files:
            if file.name == name:
                self.files.remove(file)

    def save(self):
        """Produce new Email from body, head and files, save it, delete old"""
        delete_old = deepcopy(self.uid) if self.uid else False
        self.uid = int(self.imap.save_message(str(self)))
        if delete_old:
            self.imap.delete_uid(delete_old)
        return self.uid

    def __str__(self):
        return self.plain
