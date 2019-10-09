"""Factory for Storage
This is the layer between bare Imap and the directories that hold the data
"""
from email import message_from_bytes
from .directory import Directory


class Storage:
    """Storage is the view of the IMAP directory"""
    def __init__(self, imap):
        self.imap = imap
        self._directories = None

    @property
    def directories(self):
        """ Lists of all Directory objects at this storage

        Returns:
            list: Containing Directory objects
        """
        if self._directories is None:
            folders = self.imap.list_folders()
            self._directories = sorted(
                [Directory(self, path) for path in folders]
                )
        return self._directories

    def directory_by_path(self, path):
        """
        Args:
            path(str): find directory with that path

        Returns:
            Directory: with the given path
        """
        path = self.clean_folder_path(path)
        for directory in self.directories:
            if directory.path == path:
                return directory
        return None

    def new_directory(self, path):
        """creates new directory and all subdirectories along the path
        Args:
            path(str): create directory with that path

        Returns:
            Directory: new created
        """
        path = self.clean_folder_path(path)
        splitted = path.split('.')
        for i in range(len(splitted)):
            subpath = '.'.join(splitted[0:i+1])
            self.imap.create_folder(subpath)
            directory = Directory(self, subpath)
            self.directories.append(directory)
        return directory

    def delete_directory(self, path):
        """Delete directory and its subdirectories

        Args:
            path(str): directory path to delete

        Returns:
            list: of paths(str) that have been deleted at imap
        """
        # command: LIST => Selected mailbox was deleted, have to disconnect.
        # socket error: [Errno 32] Broken pipe
        path = self.clean_folder_path(path)
        result = self.imap.delete_folder(path)
        for folder in result:
            directory = self.directory_by_path(folder)
            if directory:
                self.directories.remove(directory)
        return result

    def clean_folder_path(self, folder_name):
        """
        Args:
            folder_name(str): folder name to clean

        Returns:
            str: cleaned folder name
        """
        folder_name = folder_name.replace(
            '/', '.').replace(' ', '_').strip('.')
        if not folder_name.startswith(self.imap.config.directory):
            folder_name = '{}.{}'.format(
                self.imap.config.directory,
                folder_name,
                )
        return folder_name
        # return self.imap.clean_folder_path(folder)

    def get_heads(self, uids):
        """fetch the head of one or multiple messages

        Args:
            uids: which message heads should get fetched.
                    can be one of type(list, str, float, int)

        Returns:
            dict: with heads of uids {int(uid): str(head)}
        """
        heads = {}
        if isinstance(uids, (int, str, float)):
            uids = [str(int(uids))]
        for uid, head in self.imap.fetch(uids, 'BODY[HEADER]').items():
            heads[uid] = head[b'BODY[HEADER]'].decode('utf-8')
        return heads

    def get_bodies(self, uids):
        """fetch the body of one or multiple messages

        Args:
            uids: which message bodies should get fetched.
                    can be one of type(list, str, float, int)

        Returns:
            dict: with bodies of uids {int(uid): str(body)}
        """
        bodies = {}
        if isinstance(uids, (int, str, float)):
            uids = [str(int(uids))]
        for uid, body in self.imap.fetch(uids, 'BODY[1.1]').items():
            bodies[uid] = body[b'BODY[1.1]'].decode('utf-8')
        return bodies

    def get_file_payloads(self, uids):
        """fetch the payload of one or multiple messages
        Args:
            uids: which message payloads should get fetched.
                    can be one of type(list, str, float, int)

        Returns:
            dict: with payloads of uids {int(uid): payloads of uid}
        """
        payloads = {}
        if isinstance(uids, (int, str, float)):
            uids = [str(int(uids))]
        for uid, payload in self.imap.fetch(uids, 'RFC822').items():
            if b'RFC822' in payload:
                payloads[uid] = message_from_bytes(
                    payload[b'RFC822']
                    ).get_payload()[1:]
            else:
                payloads[uid] = []
        return payloads

    def get_subjects(self, folder=None):
        """Fetch subjects

        Args:
            folder(str, optional): select which folder you want to fetch
                subjects of. It will be created and selected if needed.

        Returns:
            dict: of subjects and uids {subject: [uid, uid]}
        """
        if folder:
            self.imap.create_folder(folder)
        subjects_cleaned = {}
        uids = self.imap.search()
        if uids:
            subjects = self.imap.fetch(
                uids,
                'BODY.PEEK[HEADER.FIELDS (SUBJECT)]'
                )
            for uid, subject in subjects.items():
                subject = message_from_bytes(
                    subject[b'BODY[HEADER.FIELDS (SUBJECT)]']
                    )['Subject']
                if subject not in subjects_cleaned:
                    subjects_cleaned[subject] = [uid]
                else:
                    subjects_cleaned[subject].append(uid)
        return subjects_cleaned

    def uninstall(self):
        """deletes the complete storage directory recursive and log out

        Returns:
            None: at the moment :TODO:
        """
        return self.imap.uninstall()
