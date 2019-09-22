from email.header import Header, decode_header
from .email import Email, new_email


class Vdir:
    """Virtual directory point of view"""
    def __init__(self, storage, subject, uid):
        self.storage = storage
        self.imap = self.storage.imap
        self.meta = VdirMeta(subject)
        self.uids = uid
        self._emails = None

    @property
    def files(self):
        files = []
        for email in self.emails:
            for file in email.xml_files:
                files.append(file)
        return sorted(files)

    @property
    def emails(self):
        if self._emails is None:
            self._emails = [Email(self, uid) for uid in self.uids]
        return self._emails

    def refresh(self, uids):
        emails = [Email(self, uid) for uid in uids]
        result = self.list_compare(self.emails, emails)
        for email in result['add']:
            self.emails.append(email)
        for email in result['rem']:
            self.emails.remove(email)
        self.uids = uids
        for email in self.emails:
            email.refresh()
        return self.emails

    def new_email(self, from_addr=None, from_displ=None):
        email = new_email(
            self.imap.config,
            self,
            from_addr=from_addr,
            from_displ=from_displ
            )
        self.emails.append(email)
        self.uids.append(email.save())
        return email

    def get_vdir_heads(self):
        heads = self.imap.get_heads(self.uids)
        for uid, head in heads.items():
            self.email_by_uid(uid).head = head
        return heads

    def get_vdir_bodies(self):
        bodies = self.imap.get_bodies(self.uids)
        for uid, body in bodies.items():
            self.email_by_uid(uid).body = body
        return bodies

    def get_vdir_file_payloads(self, uid=None):
        """
        :returns: payloads as string
        """
        uid = uid or self.uids
        return self.imap.get_file_payloads(uid)

    def email_by_uid(self, uid):
        return [email for email in self.emails if email.uid == uid][0]

    def delete(self):
        return self.imap.delete_uid(self.uids)

    @staticmethod
    def list_compare(old, new):
        """ return{'rem':[miss in new], 'add':[miss in old]} """
        return {
            'rem': [x for x in old if x not in new],
            'add': [x for x in new if x not in old]
            }

    def __hash__(self):
        return hash((self.meta.tag, self.meta.subject))

    def __lt__(self, other):
        return self.meta.item < other.meta.item

    def __eq__(self, other):
        return self.meta.subject == other.meta.subject

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.meta.subject}'

    def __str__(self):
        return self.meta.subject


class VdirMeta():
    """Tag /app/path/path/item"""
    def __init__(self, subject):
        self.subject = decode_header(subject)[0][0]
        if isinstance(self.subject, bytes):
            self.subject = self.subject.decode('utf-8')
        self.subject_encoded = Header(subject).encode()
        self.splitted = self.full_path.strip('/').split('/')

    @property
    def tag(self):
        return self.subject.split(' ', 1)[0]

    @property
    def full_path(self):
        return self.subject.split(' ', 1)[1]

    @property
    def app(self):
        splitted = self.splitted
        return splitted[0] if splitted else '/'

    @property
    def item(self):
        splitted = self.splitted
        return splitted[-1] if len(splitted) >= 2 else '/'

    @property
    def path(self):
        splitted = self.splitted
        return '/'.join(splitted[1:-1]) if len(splitted) >= 3 else '/'
