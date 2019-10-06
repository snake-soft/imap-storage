"""Imap connection class
This class represents the connection layer
Many of them are reimplementation of IMAPClient methods
"""
from builtins import ConnectionResetError
from imaplib import IMAP4
from imapclient import IMAPClient, exceptions
from imap_storage.tools import timer
__all__ = ['Imap', 'timer']


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

    def init(self):
        """initialize or reinitialize imap connection"""
        host = self.config.imap.host
        port = self.config.imap.port
        ssl_context = self.ssl_context or None
        if hasattr(self, '_imap'):
            try:
                self.logout()
            except OSError:
                pass
        super().__init__(host, port=port, ssl_context=ssl_context)

    def connect(self):
        """Connect to Imap Server with credentials from self.config.imap"""
        if not self.is_ok:
            self.init()
        if self.state == 'NONAUTH':
            self.login(self.config.imap.user, self.config.imap.password)
        if self.state == 'AUTH':
            self.create_folder(self.config.directory, connect=False)
            #self.current_folder = 'INBOX'
            #IMAPClient.select_folder(self, self.current_folder)
        if self.state != 'SELECTED':
            raise exceptions.LoginError('Unable to connect')

    @property
    def is_ok(self):
        """ test if the imap connection is ok
        :returns: True if connection is ok
        """
        if hasattr(self, '_imap'):
            socket = self._imap.socket()
        else:
            return False
        try:
            socket.getpeername()
        except OSError:
            return False
        try:
            self.noop()
        # (ConnectionResetError, AttributeError, BrokenPipeError, IMAP4.abort,)
        except (IMAP4.abort, ConnectionResetError):
            return False
        return True

    @property
    def state(self):
        """get the state of the imap connection
        :returns: IMAP4.Commands
        """
        return self._imap.state

    def clean_folder_path(self, folder):
        folder = folder.replace('/', '.').strip('.')
        if not folder.startswith(self.config.directory):
            folder = '{}.{}'.format(self.config.directory, folder)
        if folder.endswith('.'):
            folder = folder[0:-1]
        return folder

    # ### Overrides of IMAPClient methods: ###
    @timer
    def list_folders(self, connect=True):  # pylint: disable=arguments-differ
        if connect:
            self.connect()
        directory = self.config.directory
        folders = IMAPClient.list_folders(self, directory=directory)
        folders = [folder[2] for folder in folders
                   if folder[2].startswith(directory)]
        return folders

    @timer
    def create_folder(self, folder, connect=True):
        # pylint: disable=arguments-differ
        response = False
        if connect:
            self.connect()
        folder = self.clean_folder_path(folder)
        if folder not in self.list_folders(connect=connect):
            response = IMAPClient.create_folder(self, folder)
        if self.current_folder != folder:
            self.select_folder(folder, connect=connect)
        return response

    @timer
    def select_folder(self, folder, connect=True):  # pylint: disable=arguments-differ
        """selects folder if exist"""
        if connect:
            self.connect()
        folder = self.clean_folder_path(folder)
        #=======================================================================
        # if folder == self.current_folder:
        #     return True
        #=======================================================================
        try:
            response = IMAPClient.select_folder(self, folder)[b'READ-WRITE']
            self.current_folder = folder
        except IMAP4.error:
            response = False
            self.current_folder = self.config.directory
            IMAPClient.select_folder(self, self.config.directory)
        return response

    def logout(self):
        try:
            result = IMAPClient.logout(self)
        except (IMAP4.error, OSError):  # oserror is maybe true (already out)
            result = False
        return result

    @timer
    def search(self, folder=None, criteria=None, charset=None):
        # pylint: disable=arguments-differ
        """Get messages on current selected Imap folder
        criteria could also be 'ALL'
        :returns: All Message [ids] with *self.config.tag* in subject
        """
        self.connect()
        self.select_folder(folder or self.current_folder)
        criteria = criteria or ['SUBJECT', self.config.tag]
        # self.connect()
        ret = IMAPClient.search(self, criteria=criteria, charset=charset)
        return sorted([uid for uid in ret])

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
        """delete folder and all sub folders recursive
        :returns: list of deleted folders and subfolders
        """
        self.connect()
        deleted = []
        folder = self.clean_folder_path(folder)
        folders = self.list_folders()
        for fldr in folders:
            if fldr.startswith(folder) and fldr != self.config.directory:
                self.select_folder(self.config.directory)
                response = IMAPClient.delete_folder(self, fldr)
                if 'Delete completed'.encode() in response:
                    deleted.append(fldr)
        return deleted

    @timer
    def delete_messages(self, messages, silent=False):
        """delete message on the server
        :param messages: message uid(s) to delete
        :returns: bool if uids are not in self.uids anymore
        """
        self.connect()
        if isinstance(messages, (str, float, int)):
            messages = [int(messages)]
        IMAPClient.delete_messages(self, messages, silent=silent)
        self.expunge()
        return all(uid not in self.search() for uid in messages)

    @timer
    def expunge(self, messages=None):
        self.connect()
        return IMAPClient.expunge(self, messages=messages)

    def __str__(self):
        return self.config.imap.user
