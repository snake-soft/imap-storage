from . import new_email, Email


def new_directory(storage, path):
    obj = Directory(storage, path)
    storage.imap.create_folder_recursive(path)
    return obj


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

    def __hash__(self):
        return hash(self.path)

    def __lt__(self, other):
        return self.path < other.path

    def __eq__(self, other):
        return self.path == other.path

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.path}'

    def __str__(self):
        return self.path
