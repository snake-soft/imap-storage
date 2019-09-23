"""Factory for Vdir"""
from .vdir import Vdir
from .directory import Directory


class Storage:
    """Storage is the view of the IMAP directory"""
    def __init__(self, imap):
        self.imap = imap
        self._vdirs = None

    @property
    def vdirs(self):
        """Virtual directories in selected Imap folder
        :returns: list of vdir objects
        """
        if self._vdirs is None or True:
            self._vdirs = []
            self.refresh()
        return sorted(self._vdirs)

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

    # Vdir related
    def refresh(self):
        """load new state of data of all vdir objects"""
        subjects = self.imap.get_all_subjects()
        old = self._vdirs or []
        new = [Vdir(self, subject, uids) for subject, uids in subjects.items()]
        result = self.list_compare(old, new)
        for vdir in result['add']:
            self._vdirs.append(vdir)
        for vdir in result['rem']:
            self._vdirs.remove(vdir)
        for vdir in self._vdirs:
            uids = subjects[vdir.meta.subject_encoded]
            vdir.refresh(uids)

    def vdir_by_subject(self, subject, or_newdir=False):
        """
        :param subject: Subject to search
        :param or_newdir: (optional) if vdir not exists, create it
        :returns: vdir or new_vdir(optional) or false
        """
        ret = sorted(
            [vdir for vdir in self.vdirs if vdir.meta.subject == subject]
            )
        if ret:
            ret = ret[-1]
        elif or_newdir:
            ret = self.new_vdir(subject)
        else:
            ret = False
        return ret

    def new_vdir(self, subject):
        vdir = Vdir(self, subject, [])
        self.vdirs.append(vdir)
        vdir.new_email()
        self.refresh()
        if vdir.uids == []:
            raise AttributeError
        return vdir

    def email_by_uid(self, uid):
        for vdir in self.vdirs:
            if uid in vdir.uids:
                return vdir.email_by_uid(uid)

    @staticmethod
    def list_compare(old, new):
        """ return{'rem':[miss in new], 'add':[miss in old]} """
        return {
            'rem': [x for x in old if x not in new],
            'add': [x for x in new if x not in old]
            }
