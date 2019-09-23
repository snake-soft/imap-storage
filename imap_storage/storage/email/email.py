''' Email and Attachment class '''
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from copy import deepcopy

from imap_storage.storage.email.head import Head
from imap_storage.storage.email.body import Body
from imap_storage.storage.email.file import file_from_payload, file_from_xml


class Email:
    """Emails as data storage interface
    :param imap: Imap connection
    :param uid: new object if None - make sure to run *new* method
    """
    def __init__(self, directory, uid):
        self.directory = directory
        self.uid = uid
        self._head = None
        self._body = None
        self._files = None

    @property
    def head(self):
        """access to the head object, fetch if not already done"""
        if not self._head:
            self._head = self.directory.fetch_head(self)
        if isinstance(self._head, str):
            self._head = Head(self._head)
        return self._head

    @head.setter
    def head(self, head):
        if isinstance(head, Head):
            self._head = head
        elif isinstance(head, str):
            self._head = Head(head)

    def new_head(self, subject, from_addr_obj, to_addr_obj):
        """Create new message and save it
        :param subject: subject as string
        :param from_addr_obj: from-address as *Address* Object
        :param to_addr_obj: to-address as *Address* Object
        :returns: self
        """
        head = Head()
        head['From'] = str(from_addr_obj)
        head['To'] = str(to_addr_obj)
        head['Subject'] = subject
        head['Date'] = formatdate(localtime=True)
        self.head = head
        return self.head

    @property
    def body(self):
        """access to the body object, fetch if not already done"""
        if not self._body:
            self._body = self.directory.fetch_body(self)
        return self._body

    @body.setter
    def body(self, body):
        if isinstance(body, Body):
            self._body = body
        elif isinstance(body, str):
            self._body = Body(body)

    def new_body(self):
        self.body = Body(None).new()
        return self.body

    @property
    def files(self):
        """access to the file objects, fetch if not already done"""
        if self._files is None:
            self._files = []
            if self.uid:
                payloads = self.directory.fetch_payloads(self.uid)
                for payload in payloads[self.uid]:
                    if not payload['Content-Type'].startswith(
                            'multipart/alternative;'):
                        self._files.append(file_from_payload(self, payload))
        return self._files

#    @files.setter
#    def files(self, files_list):
#        self._files = files_list

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
        msg = deepcopy(self.head)
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

        files = self.files
        for file in files:
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
        return self.body.add_item(
            tag,
            text=text,
            attribs=attribs,
            parent=parent
            )

#    def remove_item(self, id_):
#        """forwards to body method"""
#        self.body.remove_item(id_)

    def add_file(self, file_obj):
        """add file to email
        :param file_obj: Object of class storage.file.File
        :returns: success bool
        """
        if file_obj.name not in [file.name for file in self.files]:  # genexp
            attribs = {
                'name': file_obj.name,
                'size': file_obj.size,
                'mime': file_obj.mime,
                }
            if file_obj.time:
                attribs['time'] = file_obj.time
            child = self.add_item('file', attribs=attribs)
            file_obj.id_ = child.attrib['id']
            self.files.append(file_obj)
            self.save()
        return file_obj in self.files

    def remove_file_by_attrib(self, attrib, value):
        """remove file from email
        eg. remove_file_by_attrib('id', 'ldsKLfds')
        :param attrib: attribute to select
        :param value: value of the attribute
        """
        for bad in self.body.xml.xpath(
                "//*[@{}=\'{}\']".format(attrib, value)):
            name = bad.get('name')
            bad.getparent().remove(bad)
        for file in self.files:
            if file.name == name:
                self.files.remove(file)
        self.save()

    def remove_file(self, file):
        self.remove_file_by_attrib('name', file.name)

    def refresh(self):
        """runned by storage refresh"""
        self._head = None
        self._body = None
        self._files = None

    def save(self):
        """Produce new Email from body, head and files, save it, delete old"""
        imap = self.directory.storage.imap
        old_uid = self.uid or False
        self.uid = int(imap.save_message(self.plain))
        if old_uid:
            imap.delete_uid(old_uid)
        self._files = None
        return self.uid

    def __hash__(self):
        return hash((self.uid))

    def __eq__(self, other):
        return self.uid == other.uid

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.uid < other.uid

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '{}: {}'.format(
            self.__class__.__name__,
            self.uid,
            )
