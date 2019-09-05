'''Imap connection class'''
from email import message_from_bytes
from imaplib import IMAP4
from imapclient import IMAPClient, exceptions
from lib.storage import Email

__all__ = ['Imap', 'timer']


def timer(func):
    """@timer decorator"""
    from functools import wraps
    from time import time

    @wraps(func)  # sets return meta to func meta
    def wrapper(*args, **kwargs):
        start = time()
        ret = func(*args, **kwargs)
        dur = format((time() - start) * 1000, ".2f")
        arg_str = ', '.join([str(arg) for arg in args]
                            +[str(k) + "=" + str(v) for k, v in kwargs.items()])
        print('%s(%s) -> %sms.' % (func.__name__, arg_str, dur))
        return ret

    return wrapper


class Imap(IMAPClient):
    """Imap connection class
    :param config: AccountConfig Object with correct data
    :param unsafe: Workaround for invalid ssl certificates (unproductive only)
    """
    def __init__(self, config, unsafe=False):
        self.config = config
        self.unsafe = unsafe
        if unsafe:
            import ssl
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        super().__init__(
            self.config.imap.host,
            port=self.config.imap.port,
            ssl_context=self.ssl_context if self.unsafe else None,
            )
        self.connect()

    @timer
    def connect(self):
        """Connect to Imap Server with credentials from self.config.imap"""
        if not hasattr(self, '_imap'):
            super().__init__(
                self.config.imap.host,
                port=self.config.imap.port,
                ssl_context=self.ssl_context if self.unsafe else None,
                )
        if self.state == 'NONAUTH':
            self.login(self.config.imap.user, self.config.imap.password)
        if self.state == 'AUTH':
            self.select_folder(self.config.directory)
        if self.state != 'SELECTED':
            raise exceptions.LoginError('Unable to connect')

    @property
    def state(self):
        return self._imap.state

    @property
    def vdirs(self):
        """Virtual directories in selected Imap folder
        :returns: dictionary key=vdirs, value=list of email objects
        """
        vdirs = {}
        subjects = self.fetch(self.uids, 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]')
        for uid, subject in subjects.items():
            subject = message_from_bytes(
                subject[b'BODY[HEADER.FIELDS (SUBJECT)]'])['Subject']
            subject = subject.lstrip(f'{self.config.tag} ')
            if subject not in vdirs:
                vdirs[subject] = [Email(self, uid)]
            else:
                vdirs[subject].append(Email(self, uid))
        return vdirs

    @property
    def emails(self):
        """
        :returns: All self.uids as emails
        """
        return [Email(self, uid) for uid in self.uids]

    @property
    def uids(self):
        """Get messages on Imap folder
        :returns: All Message [ids] with *self.config.tag* in subject
        """
        return self.search(criteria=['SUBJECT', self.config.tag])

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
        result = self.append(self.config.directory, str(msg_obj))
        # return 'Append completed.' in str(result)
        return int(result.decode('utf-8').split(']')[0].split()[-1])

    def delete_uid(self, uid):
        """delete message on the server
        :param uid: message uid to delete
        :returns: bool
        """
        self.delete_messages(uid)
        self.expunge()
        return uid not in self.uids

    # Overwrites for time measuring
    @timer
    def search(self, criteria='ALL', charset=None):
        self.connect()
        return IMAPClient.search(self, criteria=criteria, charset=charset)

    @timer
    def fetch(self, messages, data, modifiers=None):
        self.connect()
        return IMAPClient.fetch(self, messages, data, modifiers=modifiers)

    @timer
    def append(self, folder, msg, flags=(), msg_time=None):
        self.connect()
        return IMAPClient.append(
            self, folder, msg, flags=flags, msg_time=msg_time)

    @timer
    def delete_messages(self, messages, silent=False):
        self.connect()
        return IMAPClient.delete_messages(self, messages, silent=silent)

    @timer
    def expunge(self, messages=None):
        return IMAPClient.expunge(self, messages=messages)

    def __str__(self):
        return self.config.imap.user
