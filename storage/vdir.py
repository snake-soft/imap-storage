from copy import deepcopy
from email import message_from_string
from .email import Email, new_email


class Vdir:
    """Virtual directory point of view"""
    def __init__(self, imap, subject, uids):
        self.imap = imap
        self.meta = VdirMeta(subject)
        self.uids = uids
        self.emails = [Email(self, uid) for uid in self.uids]

    @property
    def files(self):
        files = []
        for email in self.emails:
            for file in email.xml_files:
                files.append(file)
        return sorted(files)

    def new_email(self, from_addr=None, from_displ=None):
        return new_email(
            self.imap.config,
            self,
            from_addr=from_addr,
            from_displ=from_displ
            )

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
        return self.imap.get_file_payloads(self.uids)

    def save_email(self, email_obj):
        """save msg_obj to imap directory
        :returns: new uid on success or False
        """
        if isinstance(email_obj, str):
            email_obj = message_from_string(email_obj)
        old_uid = deepcopy(email_obj.uid) if email_obj.uid else False
        uid = int(self.imap.save_message(email_obj.to_string()))
        if old_uid:
            self.imap.delete_uid(old_uid)
        return uid

    def email_by_uid(self, uid):
        return [email for email in self.emails if email.uid == uid][0]

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
    def __init__(self, subject):
        self.subject = subject
        self.tag, self.full_path = subject.split(' ', 1)
        splitted = self.full_path.strip('/').split('/')
        self.app = splitted[0] if splitted else '/'
        self.item = splitted[-1] if len(splitted) >= 2 else '/'
        self.path = '/'.join(splitted[1:-1]) if len(splitted) >= 3 else '/'
