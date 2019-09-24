"""Factory for Vdir"""
from imaplib import IMAP4
from .directory import Directory


class Storage:
    """Storage is the view of the IMAP directory"""
    def __init__(self, imap):
        self.imap = imap

    @property
    def directories(self):
        """
        :param path: relative to the base path from self.imap.config.directory
        :returns: list of Directory objects
        """
        folders = self.imap.folders
        return sorted([Directory(self, path) for path in folders])

    def directory_by_path(self, path):
        path = self.clean_folder_path(path)
        for directory in self.directories:
            if directory.path == path:
                return directory
        return None

    def new_directory(self, path):
        self.imap.create_folder_recursive(path)
        return Directory(self, path)

    def delete_directory(self, path):
        try:
            result = self.imap.delete_folder(path)
        except IMAP4.error:
            return False
        return 'Delete completed '.encode() in result

    def clean_folder_path(self, folder):
        return self.imap.clean_folder_path(folder)
