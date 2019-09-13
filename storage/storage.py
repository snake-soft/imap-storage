"""Interface of the Storage Module"""
from email import message_from_bytes
from collections import OrderedDict
from . import Vdir, Email


class Storage:
    def __init__(self, imap):
        self.imap = imap

    @property
    def vdirs(self):
        """Virtual directories in selected Imap folder
        :returns: dictionary key=vdirs, value=list of email objects
        """
        vdirs = {}
        subjects = self.imap.get_all_subjects()
        for uid, subject in subjects.items():
            try:
                subject = message_from_bytes(
                    subject[b'BODY[HEADER.FIELDS (SUBJECT)]']
                    )['Subject']
                #subject = subject.lstrip(f'{self.config.tag} ')
            except (TypeError, KeyError) as error:
                import pdb; pdb.set_trace()  # <---------

            vdir = Vdir(subject)

            vdirs[vdir] = []
            vdirs[vdir].append(Email(self.imap, uid))
        vdir.emails = [] # ###
        return OrderedDict(sorted(vdirs.items(), key=lambda t: t[0]))

    @property
    def vdirs_files(self):
        vdirs_files = {}
        for vdir, vdir_emails in self.vdirs.items():
            vdirs_files[vdir] = []
            for email in vdir_emails:
                for file in email.xml_files:
                    vdirs_files[vdir].append(file)
            vdirs_files[vdir] = sorted(vdirs_files[vdir])
        return OrderedDict(sorted(vdirs_files.items(), key=lambda t: t[0]))

    @property
    def emails(self):
        """
        :returns: All self.uids as emails
        """
        return [Email(self.imap, uid) for uid in self.imap.uids]

    def vdir_by_path(self, path):
        """filters self.vdirs, not used"""
        path = '%s%s%s' % (
            '/' if path[0] != '/' else '',
            path,
            '/' if path[-1] != '/' else '',
            )
        return self.vdirs[f'{path}']

    def email_by_uid(self, uid):
        """Get email by uid
        :param uid: uid to return
        :returns: first found email object with uid
        """
        return [email for email in self.emails if email.uid == uid][0]

    def save_message(self, msg_obj):
        """save msg_obj to imap directory
        :returns: new uid on success or False
        """
        return self.imap.save_message(msg_obj)

    def delete_uid(self, uid):
        """delete message on the server
        :param uid: message uid to delete
        :returns: bool
        """
        return self.imap.delete_uid(uid)
