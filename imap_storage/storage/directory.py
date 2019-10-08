"""Directory class
This represents a physical directory at storage level (imap)
"""
from .email.email import Email
from .email.address import Address
from ..tools.compare import list_compare


class Directory:  # :TODO: # pylint: disable=too-many-public-methods
    """Directory class"""
    def __init__(self, storage, folder):
        self.storage = storage
        self.imap = storage.imap
        if ' ' in folder:
            folder = folder.replace(' ', '_')
        self.folder = folder
        self.path = folder
        self._emails = None
        self._uids = None

    @property
    def parent(self):
        """parent directory

        Returns:
            Directory:
        """
        splitted = self.path.split('.')
        if len(splitted) > 1:
            path = '.'.join(splitted[:-1])
            directory = self.storage.directory_by_path(path)
        else:
            directory = None
        return directory

    @property
    def childs(self):
        """childs of this directory

        Returns:
            list: of directories [Directory, ...]
        """
        dirs = []
        for directory in self.storage.directories:
            path = directory.path
            is_subdir = len(self.path.split('.'))+1 == len(path.split('.'))
            if path.startswith(self.path) and is_subdir:
                dirs.append(self.storage.directory_by_path(path))
        return dirs

    @property
    def breadcrumbs(self):
        """path of this directory in breadcrumb format

        Returns:
            list: [self.parent.parent.parent, self.parent.parent, self.parent]
        """
        breadcrumbs = []
        directory_iter = self
        while directory_iter.parent:
            directory_iter = directory_iter.parent
            breadcrumbs.append(directory_iter)
        return sorted(breadcrumbs)

    @property
    def uids(self):
        """keep this uptodate because self.emails compares to it"""
        if self._uids is None or True:  # ever refreshing
            self.imap.create_folder(self.path)
            self._uids = self.imap.search()
        return self._uids

    @property
    def emails(self):
        """cannot be dynamic because of self.fetch methods"""
        if self._emails is None:
            self._emails = [Email(self, uid) for uid in self.uids]
        else:
            email_uids = [email.uid for email in self._emails if email.uid]
            rem, add = list_compare(email_uids, self.uids)
            for uid in rem:
                self._emails.remove(Email(self, uid))
            for uid in add:
                self._emails.append(Email(self, uid))
        return self._emails

    @property
    def files(self):
        """List files of all emails inside this directory

        Returns:
            list: of files
        """
        files = []
        for email in self.emails:
            for file in email.files:
                files.append(file)
        return files

    @property
    def app_name(self):  # :TODO:
        """the name of the application of this directory

        Returns:
            str:
        """
        splitted = self.path.split('.')
        return splitted[1] if len(splitted) > 1 else splitted[0]

    @property
    def item_name(self):  # :TODO:
        """this is the name of the item

        Returns:
            str
        """
        return self.path.split('.')[-1]

    @property
    def url(self):
        """makes the Django life easier

        Returns:
            str: path as url
        """
        directory = self.imap.config.directory
        if self.path.startswith(directory):
            url = self.path[len(directory)+1:]
        else:
            url = self.path
        return url.replace('.', '/')

    def refresh(self):
        """refresh the directories cached properties"""
        self._uids = None

    def email_by_uid(self, uid):
        """get email by uid

        Args:
            uid(int): uid you want to have the email object

        Returns:
            Email: if email with uid exists in this directory or None
        """
        uid = int(uid)
        for email in self.emails:
            if email.uid == uid:
                return email
        return None

    def add_file_email(self, file):
        """Create new Email with one file

        Args:
            file(File): object to append as file to the directory

        Returns:
            Email: new created file Email
        """
        if file.name in [file.name for file in self.files]:
            return False
        email = self.new_email(file.name)
        email.add_file(file)
        email.save()
        self.refresh()
        return self.email_by_uid(email.uid)

    def file_by_name(self, name):
        """get file by name

        Args:
            name(str): name of the file to get

        Returns:
            File: first file with name
        """
        for file in self.files:
            if file.name == name:
                return file
        return False

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
        return email

    def delete_email(self, email_uid_or_obj):
        """delete email within this directory

        Args:
            email_uid_or_obj(Email, int, str): email to delete

        Returns:
            bool: True if success
        """
        if isinstance(email_uid_or_obj, Email):
            uid = email_uid_or_obj.uid
        else:
            uid = email_uid_or_obj
        result = self.imap.delete_messages([uid])  # immer true :-(
        return result

    def delete(self):
        """Delete this storage

        Warning:
            Also deletes its subdirectories recursively

        Returns:
            bool: True if success
        """
        return self.storage.delete_directory(self.path)

    # ### Fetch methods ###
    def fetch_subjects(self, email=None):
        """fetch subjects

        Args:
            email(Email, optional): fetch only from this email

        Returns:
            dict: {uid: subject}
        """
        if email:
            uids = [email.uid]
        else:
            uids = self.uids
        subjects = self.storage.get_subjects(folder=self.path)
        for subject, uids in subjects.items():
            for uid in uids:
                self.email_by_uid(uid).subject = subject
        return subjects

    def fetch_head(self, email):
        """fetch email head

        Args:
            email(Email): fetch head of this email

        Returns:
            str: head of email
        """
        return self.storage.get_heads(email.uid)[email.uid]

    def fetch_body(self, email):
        """fetch email body

        Args:
            email(Email): fetch body of this email

        Returns:
            str: body of email
        """
        return self.storage.get_bodies(email.uid)[email.uid]

    def fetch_payloads(self, email):
        """
        :returns: payloads as string
        """
        return self.storage.get_file_payloads(email.uid)[email.uid]

    def save_message(self, msg_obj):
        """save msg_obj to imap directory
        :returns: new uid on success or False
        """
        old_uid = msg_obj.uid
        result = self.imap.append(self.folder, str(msg_obj.plain))
        if old_uid:
            self.imap.delete_messages(old_uid)
        self.refresh()
        return int(result.decode('utf-8').split(']')[0].split()[-1])

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
