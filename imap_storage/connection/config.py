"""Account config class"""
__all__ = ['Config']


class Config:
    """Account Configuration class"""
    TAG = 'IMAP-Storage'

    def __init__(self):
        self.imap = _ImapConfig()
        self.smtp = _SmtpConfig()

        self.directory = 'storage'
        self.tag = self.TAG
        self.domain = None

    @property
    def is_ok(self):
        return all((self.imap.is_ok, self.smtp.is_ok, self.tag))

    @classmethod
    def from_request(cls, request):
        config = cls()
        config.imap.user = request.session.get('imap_user')
        config.imap.password = request.session.get('imap_password')
        config.imap.host = request.session.get('imap_host')
        config.imap.port = request.session.get('imap_port', 993)

        return config if config.is_ok else None

    def __str__(self):
        return '{}, {}'.format(str(self.imap), str(self.smtp))


class _ImapConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = 993

    @property
    def is_ok(self):
        return all((self.user, self.password, self.host, self.port))

    def __str__(self):
        return str(self.user)


class _SmtpConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = 465

    @property
    def is_ok(self):
        # return all(self.user, self.password)
        return True

    def __str__(self):
        return str(self.user)
