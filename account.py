from .connection import Config, Imap
from .storage import Storage
from imapclient.exceptions import LoginError


class AccountFactory:
    def __init__(self):
        self._accounts = {}

    @property
    def accounts(self):
        return self._accounts

    def new(self, id_, config):
        new_acc = Account(id_, config)
        if new_acc.is_ok:
            self.accounts[id_] = new_acc
            return new_acc
        else:
            return False

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
                account = self.new(session_key, config)

        return account or None


class Account:
    def __init__(self, id_, config):
        self.id_ = id_
        self.config = config
        self.imap = Imap(config, unsafe=True)
        self.smtp = None
        self.storage = Storage(self.imap)

    @property
    def is_ok(self):
        try:
            self.imap.login(self.config.imap.user, self.config.imap.password)
        except LoginError:
            return False
        return True

    def close(self):
        return self.imap.logout() == b'Logging out'
