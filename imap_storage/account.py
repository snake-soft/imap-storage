from imapclient.exceptions import LoginError
from .connection.config import Config
from .connection.imap import Imap
from .storage.storage import Storage

__all__ = ['AccountManager', 'Account']


class AccountManager:
    """ manager (factory class) for Account class"""
    def __init__(self):
        self._accounts = {}

    @property
    def accounts(self):
        return self._accounts

    def new(self, config, id_):
        self.accounts[id_] = Account(config, id_)
        return self.accounts[id_]

    def by_id(self, id_):
        return self.accounts.get(id_, None)

    def by_request(self, request):
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        account = self.by_id(session_key)  # None if not exists

        if not account:
            config = Config().from_request(request)
            if config:
                account = self.new(config, session_key)

        return account or None


class Account:
    """Use this if you only need one account or if you have another manager"""
    def __init__(self, config, id_, unsafe=False):
        self.id_ = id_
        self.config = config
        self.imap = Imap(config, unsafe)
        self.smtp = None
        self.storage = Storage(self.imap)

    @property
    def is_ok(self):
        return True  # self.imap._imap.check()[0] == 'OK'

    def close(self):
        return self.imap.logout() == b'Logging out'

    def __lt__(self, other):
        return self.id_ < other.id_

    def __eq__(self, other):
        return self.id_ == other.id_

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'Account: {}'.format(str(self))

    def __str__(self):
        return str(self.id_)
