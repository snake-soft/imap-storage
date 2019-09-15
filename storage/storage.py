"""Factory for Vdir"""
from .vdir import Vdir


class Storage:
    """Storage is the view of the IMAP directory"""
    def __init__(self, imap):
        self.imap = imap
        # self._subjects = []

    @property
    def vdirs(self):
        """Virtual directories in selected Imap folder
        :returns: list of vdir objects
        """
        vdirs = []
        subjects = self.imap.get_all_subjects()
        for subject, uids in subjects.items():
            vdirs.append(Vdir(self.imap, subject, uids))
        return sorted(vdirs)

    @property
    def emails(self):
        emails = []
        for vdir in self.vdirs:
            emails.extend(vdir.emails)
        return sorted(emails)

    #===========================================================================
    # def email_by_uid(self, uid):
    #     return [email for email in self.emails if email.uid == uid][0]
    #===========================================================================

    def vdir_by_subject(self, subject):
        for vdir in self.vdirs:
            if vdir.meta.subject == subject:
                return vdir

    def new_vdir(self, subject):
        return Vdir(self.imap, subject, [])

    def email_by_uid(self, uid):
        for vdir in self.vdirs:
            if uid in vdir.uids:
                return vdir.email_by_uid(uid)

    #===========================================================================
    # def delete_uid(self, uids):
    #     """delete message on the server
    #     :param uid: message uid to delete
    #     :returns: bool
    #     """
    #     return self.imap.delete_uid(uids)
    #===========================================================================
