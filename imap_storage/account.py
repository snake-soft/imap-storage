"""Account and AccountManager class
Use one of them to manage your imap_storage connection(s)
"""
from .connection.config import Config
from .connection.imap import Imap
from .storage.storage import Storage

__all__ = ['AccountManager', 'Account']


class AccountManager:
    """If you work with multiple accounts in parallel you should use this
    It is a factory class for Account
    """
    def __init__(self):
        self._accounts = {}

    @property
    def accounts(self):
        """
        :returns: the whole dictionary of Accounts
        """
        return self._accounts

    def new(self, config, id_):
        """Create a new Account
        :param config: Config object
        :param id_: Id to store the account with
        :returns: New created account
        """
        self.accounts[id_] = Account(config, id_)
        return self.accounts[id_]

    def by_id(self, id_):
        """Get account object by id
        :param id_: Id of the Account
        :returns: Account object
        """
        return self.accounts.get(id_, None)

    def by_request(self, request):
        """Get account object by django request
        :param request: Django request to access the account of the session
        :returns: Account that belongs to the session
        """
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

    def is_ok(self):
        """Tests if the Account is ok
        :returns: True if the imap connection of the account is ok
        """
        return self.imap.is_ok()

    def close(self):
        """close the account connection
        :returns: True if imap logged out
        """
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
