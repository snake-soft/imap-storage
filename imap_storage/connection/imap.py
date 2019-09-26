"""Imap connection class"""
import sys
from builtins import ConnectionResetError, BrokenPipeError
from imaplib import IMAP4
from imapclient import IMAPClient, exceptions
from email import message_from_bytes
__all__ = ['Imap', 'timer']


def timer(func):
    """@timer decorator
    :TODO: option to shorten args at output
    """
    from functools import wraps
    from time import time

    @wraps(func)  # sets return meta to func meta
    def wrapper(*args, **kwargs):
        start = time()
        ret = func(*args, **kwargs)
        dur = format((time() - start) * 1000, ".2f")
        arg_str = ', '.join([str(arg) for arg in args]
                            + [str(k) + "=" + str(v)
                               for k, v in kwargs.items()])
        #=======================================================================
        # if sys.argv[0] != 'mod_wsgi':
        #     if len(sys.argv) >=2 and sys.argv[1] != 'test' or sys.argv[0]=='main.py':
        #=======================================================================
        print('%s(%s) -> %sms.' % (func.__name__, arg_str, dur))
        return ret
    return wrapper


class Imap(IMAPClient):
    """Imap connection class
    :param config: Config Object with correct data
    :param unsafe: Workaround for invalid ssl certificates (unproductive only)
    """
    def __init__(self, config, unsafe=False):  # pylint: disable=W0231
        self.config = config
        self.unsafe = unsafe
        if unsafe:
            import ssl
            self.ssl_context = ssl.create_default_context()
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            self.ssl_context = None
        self.current_folder = None
        self.init()
        self.connect()
        self._folders = None

    def connect(self):
        """Connect to Imap Server with credentials from self.config.imap"""
        possible_errors = (
                ConnectionResetError,
                AttributeError,
                BrokenPipeError,
                IMAP4.abort,
                )
        try:
            self.noop()
            if self.state == 'NONAUTH':
                self.login(self.config.imap.user, self.config.imap.password)
            if self.state == 'AUTH':
                self.select_folder_or_create(self.config.directory)
            if self.state != 'SELECTED':
                raise exceptions.LoginError('Unable to connect')

        except (ConnectionResetError, BrokenPipeError, IMAP4.abort):
            self.init()
            self.connect()

    def init(self):
        super().__init__(
            self.config.imap.host,
            port=self.config.imap.port,
            ssl_context=self.ssl_context or None,
            )

    @property
    def folders(self):
        if self._folders is None:
            self.connect()
            directory = self.config.directory
            folders = [folder[2] for folder in self.list_folders()
                       if folder[2].startswith(directory)]
            self._folders = folders
        return self._folders

    def select_folder_or_create(self, folder):
        """
        :returns: True if folder selected and is rw
        """
        folder = self.clean_folder_path(folder)
        self.create_folder_recursive(folder)
        if self.current_folder != folder:
            self.select_folder(folder)
        return self.current_folder

    def create_folder_recursive(self, folder):
        folder = self.clean_folder_path(folder)
        splitted = folder.split('.')
        for i in range(len(splitted)):
            folder_step = '.'.join(splitted[0:i+1])
            try:
                self.create_folder(folder_step)
            except IMAP4.error:
                pass

    def clean_folder_path(self, folder):
        folder = folder.replace('/', '.').strip('.')
        if not folder.startswith(self.config.directory):
            folder = '{}.{}'.format(
                self.config.directory,
                folder,
                )
        return folder

    def get_subjects(self, folder=None):
        """
        :returns: dict of subjects and uids {subject: [uid, uid]}
        """
        if folder:
            self.select_folder_or_create(folder)
        subjects_cleaned = {}
        uids = self.uids
        if uids:
            subjects = self.fetch(
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
    get_all_subjects = get_subjects

    @property
    def state(self):
        return self._imap.state

    @property
    def uids(self):
        """Get messages on current selected Imap folder
        :returns: All Message [ids] with *self.config.tag* in subject
        """
        ret = self.search(criteria=['SUBJECT', self.config.tag])
        return sorted([uid for uid in ret])

    def get_heads(self, uids):
        """
        :returns: dict of heads of uids {int(uid): str(head)}
        """
        heads = {}
        if isinstance(uids, (int, str, float)):
            uids = [str(int(uids))]
        for uid, head in self.fetch(uids, 'BODY[HEADER]').items():
            heads[uid] = head[b'BODY[HEADER]'].decode('utf-8')
        return heads

    def get_bodies(self, uids):
        """
        :returns: dict of bodies of uids {int(uid): str(body)}
        """
        bodies = {}
        if isinstance(uids, (int, str, float)):
            uids = [str(int(uids))]
        for uid, body in self.fetch(uids, 'BODY[1.1]').items():
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
        for uid, payload in self.fetch(uids, 'RFC822').items():
            if b'RFC822' in payload:
                payloads[uid] = message_from_bytes(
                    payload[b'RFC822']
                    ).get_payload()[1:]
            else:
                payloads[uid] = []
        return payloads

    def save_message(self, msg_obj):
        """save msg_obj to imap directory
        :returns: new uid on success or False
        """
        result = self.append(self.current_folder, str(msg_obj))
        return int(result.decode('utf-8').split(']')[0].split()[-1])

    def delete_uid(self, uids):
        """delete message on the server
        :param uid: message uid to delete
        :returns: bool
        """
        if isinstance(uids, (str, float, int)):
            uids = [int(uids)]
        self.delete_messages(uids)
        self.expunge()
        return all(uid not in self.uids for uid in uids)

    # ### Overrides of IMAPClient methods: ###
    @timer
    def list_folders(self, directory="", pattern="*"):
        return IMAPClient.list_folders(
            self, directory=directory, pattern=pattern
            )

    @timer
    def create_folder(self, folder):
        result = IMAPClient.create_folder(self, folder)
        self.select_folder(folder)
        self.folders.append(folder)
        return result

    @timer
    def select_folder(self, folder, readonly=False):
        folder = self.clean_folder_path(folder)
        if folder == self.current_folder:
            return True
        response = IMAPClient.select_folder(self, folder, readonly=readonly)
        if response[b'READ-WRITE']:
            self.current_folder = folder
        return response[b'READ-WRITE']

    @timer
    def search(self, criteria='ALL', charset=None):
        self.connect()
        return IMAPClient.search(self, criteria=criteria, charset=charset)

    @timer
    def fetch(self, messages, data, modifiers=None):
        self.connect()
        if not messages:
            raise AttributeError('No message uids')
        return IMAPClient.fetch(self, messages, data, modifiers=modifiers)

    @timer
    def append(self, folder, msg, flags=(), msg_time=None):
        self.connect()
        return IMAPClient.append(
            self, folder, msg, flags=flags, msg_time=msg_time
            )

    @timer
    def delete_folder(self, folder):
        folder = self.clean_folder_path(folder)
        return IMAPClient.delete_folder(self, folder)

    @timer
    def delete_messages(self, messages, silent=False):
        self.connect()
        return IMAPClient.delete_messages(self, messages, silent=silent)

    @timer
    def expunge(self, messages=None):
        return IMAPClient.expunge(self, messages=messages)

    def __str__(self):
        return self.config.imap.user
