"""Factory for Vdir"""
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
            folders = self.imap.folders
            self._directories = sorted([Directory(self, path) for path in folders])
        return self._directories

    def directory_by_path(self, path):
        path = self.clean_folder_path(path)
        for directory in self.directories:
            if directory.path == path:
                return directory
        return None

    def new_directory(self, path):
        path = self.clean_folder_path(path)
        self.imap.create_folder_recursive(path)
        directory = Directory(self, path)
        self.directories.append(directory)
        return directory

    def delete_directory(self, path):
        try:
            result = self.imap.delete_folder(path)
        except IMAP4.error:
            return False
        return 'Delete completed '.encode() in result

    def clean_folder_path(self, folder):
        return self.imap.clean_folder_path(folder)
