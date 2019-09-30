"""Factory for Storage"""
from email import message_from_bytes
from imaplib import IMAP4
from .directory import Directory


class Storage:
    """Storage is the view of the IMAP directory"""
    def __init__(self, imap):
        self.imap = imap
        self._directories = None

    @property
    def directories(self):
        """
        :param path: relative to the base path from self.imap.config.directory
        :returns: list of Directory objects
        """
        if self._directories is None:
            folders = self.imap.list_folders()
            self._directories = sorted(
                [Directory(self, path) for path in folders]
                )
        return self._directories

    def directory_by_path(self, path):
        path = self.clean_folder_path(path)
        for directory in self.directories:
            if directory.path == path:
                return directory
        return None

    def new_directory(self, path):
        path = self.clean_folder_path(path)
        self.imap.create_folder(path)
        directory = Directory(self, path)
        self.directories.append(directory)
        return directory

    def delete_directory(self, path):
        # command: LIST => Selected mailbox was deleted, have to disconnect.
        # socket error: [Errno 32] Broken pipe
        path = self.clean_folder_path(path)
        result = self.imap.delete_folder(path)
        if result and self.directories:
            self._directories.remove(self.directory_by_path(path))
        return result

    def clean_folder_path(self, folder):
        folder = folder.replace('/', '.').strip('.')
        if not folder.startswith(self.imap.config.directory):
            folder = '{}.{}'.format(
                self.imap.config.directory,
                folder,
                )
        return folder
        # return self.imap.clean_folder_path(folder)

    def get_heads(self, uids):
        """
        :returns: dict of heads of uids {int(uid): str(head)}
        """
        heads = {}
        if isinstance(uids, (int, str, float)):
            uids = [str(int(uids))]
        for uid, head in self.imap.fetch(uids, 'BODY[HEADER]').items():
            heads[uid] = head[b'BODY[HEADER]'].decode('utf-8')
        return heads

    def get_bodies(self, uids):
        """
        :returns: dict of bodies of uids {int(uid): str(body)}
        """
        bodies = {}
        if isinstance(uids, (int, str, float)):
            uids = [str(int(uids))]
        for uid, body in self.imap.fetch(uids, 'BODY[1.1]').items():
            bodies[uid] = body[b'BODY[1.1]'].decode('utf-8')
        return bodies

    def get_file_payloads(self, uids):
        """get payload of the files
        :param uid: uid of the message to fetch
        :returns: payloads --> {uid: message_object}
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
        """
        :returns: dict of subjects and uids {subject: [uid, uid]}
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
