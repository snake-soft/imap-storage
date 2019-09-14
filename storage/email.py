''' Email and Attachment class '''
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .head import Head, new_head
from .address import Address
from .body import Body, new_body
from .file import file_from_payload, file_from_xml

__all__ = ['Email']


def new_email(config, vdir, from_addr=None, from_displ=None):
    """needs to be runned if its a ne Email with no uid"""
    from_addr_obj = Address(
        addr_spec=from_addr or config.imap.user,
        display_name=from_displ or config.imap.user
        )
    to_addr_obj = Address(
        addr_spec=config.imap.user,
        display_name=config.imap.user
        )
    email = Email(vdir, None)
    email.head = new_head(vdir.meta.subject, from_addr_obj, to_addr_obj)
    email.body = new_body()
    return email


class Email:
    """Emails as data storage interface
    :param imap: Imap connection
    :param uid: new object if None - make sure to run *new* method
    """
    def __init__(self, vdir, uid):
        #self.imap = imap
        self.vdir = vdir
        self.uid = uid
        self._head = None
        self._body = None
        self._files = []

    @property
    def head(self):
        """access to the head object, fetch if not already done"""
        if not self._head:
            #===================================================================
            # import pdb; pdb.set_trace()  # <---------
            # head = self.imap.fetch(self.uid, 'BODY[HEADER]')[self.uid][b'BODY[HEADER]']
            # self._head = Head(message_from_bytes(head))
            #===================================================================
            self.vdir.get_vdir_heads()
        return self._head

    @head.setter
    def head(self, head):
        if isinstance(head, Head):
            self._head = head
        elif isinstance(head, str):
            self._head = Head(head)

    @property
    def body(self):
        """access to the body object, fetch if not already done"""
        if not self._body:
            self.vdir.get_vdir_bodies()  # self.uid)
            #self._body = Body(self, self.imap.get_bodies(self.uid)[self.uid])
        return self._body

    @body.setter
    def body(self, body):
        if isinstance(body, Body):
            self._body = body
        elif isinstance(body, str):
            self._body = Body(body)

    @property
    def files(self):
        """access to the file objects, fetch if not already done"""
        if self.uid and not self._files:
            payloads = self.vdir.get_vdir_file_payloads(self.uid)
            for payload in payloads[self.uid]:
                self._files.append(file_from_payload(self, payload))
        return self._files

    @property
    def xml_files(self):
        """
        :returns: list of files
        """
        files = [file_from_xml(self, file)
                 for file in self.body.get_by_tag('file')]
        return sorted(files)

    @property
    def plain(self):
        """ untested, unused """
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
        for file in self.xml_files:
            if file.id_ == id_:
                return self.file_by_name(file.name)

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
                'mime': file_obj.mime,
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
        email = self
        email.uid = email.vdir.save_email(email)
        return self.uid

    def __lt__(self, other):
        return self.uid < other.uid

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.__class__.__name__}: {self.uid}'
