from .email.email import Email
from .email.address import Address


class Directory:
    def __init__(self, storage, folder):
        self.storage = storage
        self.imap = storage.imap
        if ' ' in folder:
            raise AttributeError('Directory path should not contain spaces')
        self.folder = folder
        self.path = folder
        self._emails = None
        self._uids = None

    @property
    def parent(self):
        splitted = self.path.split('.')
        if len(splitted) > 1:
            path = '.'.join(splitted[:-1])
            directory = self.storage.directory_by_path(path)
        else:
            directory = None
        return directory

    @property
    def childs(self):
        dirs = []
        for path in self.imap.folders:
            if path.startswith(self.path) and path != self.path:
                dirs.append(self.storage.directory_by_path(path))
        return dirs

    @property
    def breadcrumbs(self):
        breadcrumbs = []
        directory_iter = self
        while directory_iter.parent:
            directory_iter = directory_iter.parent
            breadcrumbs.append(directory_iter)
        return sorted(breadcrumbs)

    @property
    def uids(self):
        if self._uids is None:
            self.imap.select_folder_or_create(self.path)
            self._uids = self.imap.uids
        return self._uids

    @property
    def emails(self):
        if self._emails is None:
            self._emails = [Email(self, uid) for uid in self.uids]
        return self._emails

    @property
    def app_name(self):
        splitted = self.path.split('.')
        return splitted[1] if len(splitted) > 1 else ''

    @property
    def item_name(self):
        return self.path.split('.')[-1]

    @property
    def url(self):
        directory = self.imap.config.directory
        if self.path.startswith(directory):
            url = self.path[len(directory)+1:]
        else:
            url = self.path
        return url.replace('.', '/')

    def email_by_uid(self, uid):
        uid = int(uid)
        for email in self.emails:
            if email.uid == uid:
                return email

    def add_file_email(self, file):
        """Create new Email with one file"""
        email = self.new_email(file.name)
        email.add_file(file)
        email.save()

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
        # email.save()
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

    # ### Fetch methods ###
    def fetch_subjects(self, email=None):
        if email:
            uids = [email.uid]
        else:
            uids = self.uids
        subjects = self.imap.get_all_subjects(folder=self.path)
        for subject, uids in subjects.items():
            for uid in uids:
                self.email_by_uid(uid).subject = subject

    def fetch_head(self, email):
        return self.imap.get_heads(email.uid)[email.uid]

    def fetch_body(self, email):
        return self.imap.get_bodies(email.uid)[email.uid]

    def fetch_payloads(self, email):
        """
        :returns: payloads as string
        """
        try:
            return self.imap.get_file_payloads(email.uid)[email.uid]
        except:
            import pdb; pdb.set_trace()  # <---------

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
