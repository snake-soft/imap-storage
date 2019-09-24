from .email.email import Email
from .email.address import Address


class Directory:
    def __init__(self, storage, path):
        self.storage = storage
        self.imap = storage.imap
        self.path = path
        self._emails = None
        self._uids = None

    @property
    def uids(self):
        self.imap.select_folder(self.path)
        return self.imap.uids

    @property
    def emails(self):
        if self._emails is None:
            self._emails = [Email(self, uid) for uid in self.uids]
        return self._emails

    @property
    def appname(self):
        return self.path.split('.')[0]

    def fetch_head(self, email):
        return self.imap.get_heads(email.uid)[email.uid]

    def fetch_body(self, email):
        return self.imap.get_bodies(email.uid)[email.uid]

    def fetch_payloads(self, email):
        """
        :returns: payloads as string
        """
        return self.imap.get_file_payloads(email.uid)[email.uid]

    def new_email(self, item_name, from_addr=None, from_displ=None):
        """needs to be runned if its a ne Email with no uid"""
        config = self.storage.imap.config
        from_addr_obj = Address(
            addr_spec=from_addr or config.imap.user,
            display_name=from_displ or config.imap.user
            )
        to_addr_obj = Address(
            addr_spec=config.imap.user,
            display_name=config.imap.user
            )
        email = Email(self, None)
        email.head = email.new_head(
            '{} {}'.format(self.imap.config.tag, item_name),
            from_addr_obj,
            to_addr_obj
            )
        email.body = email.new_body()
        email.save()
        self.emails.append(email)
        return email

    def delete_email(self, email_uid_or_obj):
        if isinstance(email_uid_or_obj, Email):
            uid = email_uid_or_obj.uid
        else:
            uid = email_uid_or_obj
        result = self.imap.delete_uid([uid])  # immer true :-(
        self.emails.remove(Email(self, uid))
        return result

    def __hash__(self):
        return hash(self.path)

    def __lt__(self, other):
        return self.path < other.path

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__, self.path)

    def __str__(self):
        return self.path
