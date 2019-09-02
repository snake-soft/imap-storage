"""Account config class"""
__all__ = ['AccountConfig']


class AccountConfig:  # pylint: disable=too-few-public-methods
    '''Account Configuration class'''
    def __init__(self):
        self.imap = _ImapConfig()
        self.smtp = _SmtpConfig()

        self.directory = 'chat'
        self.tag = 'DjangoTest'
        self.domain = None

    def __str__(self):
        return f'{self.imap}, {self.smtp}'


class _ImapConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = None

    def __str__(self):
        return self.user


class _SmtpConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = None

    def __str__(self):
        return self.user
