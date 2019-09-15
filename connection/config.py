"""Account config class"""
__all__ = ['Config']


class Config:
    """Account Configuration class"""
    TAG = 'DjangoTest'

    def __init__(self):
        self.imap = _ImapConfig()
        self.smtp = _SmtpConfig()

        self.directory = 'chat'
        self.tag = self.TAG
        self.domain = None

    @property
    def is_ok(self):
        return all((self.imap.is_ok, self.smtp.is_ok, self.tag))

    def from_request(self, request):
        if all(x in request.session for x in ['imap_user', 'imap_password']):
            config = __class__()#Config()
            config.imap.user = request.session['imap_user']
            config.imap.password = request.session['imap_password']
            config.imap.host = 'imap.hennige-it.de'
            config.imap.port = 993
            #config.tag = self.TAG
            return config
        return None

    def __str__(self):
        return f'{str(self.imap)}, {str(self.smtp)}'


class _ImapConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = None

    @property
    def is_ok(self):
        return all((self.user, self.password))

    def __str__(self):
        return str(self.user)


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
        return str(self.user)
