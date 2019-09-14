from .connection import Config, Imap
from .storage import Storage


class AccountFactory:
    def __init__(self):
        self._accounts = {}

    @property
    def accounts(self):
        return self._accounts

    def new(self, id_, config):
        new_acc = Account(id_, config)
        self.accounts[id_] = new_acc
        return new_acc

    def by_id(self, id_):
        return self.accounts.get(id_, None)


class Account:
    def __init__(self, id_, config):
        self.id_ = id_
        self.config = config
        self.imap = Imap(config, unsafe=True)
        self.smtp = None
        self.storage = Storage(self.imap)
