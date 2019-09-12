"""Account config class"""
__all__ = ['AccountConfig']


class AccountConfig:  # pylint: disable=too-few-public-methods
    '''Account Configuration class'''
    def __init__(self):
        self.imap = _ImapConfig()
        self.smtp = _SmtpConfig()

        self.directory = 'chat'
        self.tag = None
        self.domain = None

    @property
    def is_ok(self):
        return all((self.imap.is_ok, self.smtp.is_ok, self.tag))

    def __str__(self):
        return f'{self.imap}, {self.smtp}'


class _ImapConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = None

    @property
    def is_ok(self):
        return all(self.user, self.password)

    def __str__(self):
        return self.user


class _SmtpConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = None

    @property
    def is_ok(self):
        #return all(self.user, self.password)
        return True

    def __str__(self):
        return self.user
