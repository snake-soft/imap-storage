"""Factory for Vdir"""
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
        return [Directory(self, path) for path in folders]

    def directory_by_path(self, path):
        for directory in self.directories:
            if directory.path == path:
                return directory
        return None

    def new_directory(self, path):
        self.imap.create_folder_recursive(path)
        return Directory(self, path)

    @staticmethod
    def list_compare(old, new):
        """ return{'rem':[miss in new], 'add':[miss in old]} """
        return {
            'rem': [x for x in old if x not in new],
            'add': [x for x in new if x not in old]
            }
