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
        if all(x in request.session for x in ['imap_user', 'imap_password']):
            config = cls()
            config.imap.user = request.session['imap_user']
            config.imap.password = request.session['imap_password']
            config.imap.host = request.session['imap_host']
            config.imap.port = request.session['imap_port']

            config.smtp.user = request.session['imap_user']
            config.smtp.password = request.session['imap_password']
            config.smtp.host = request.session['smtp_host']
            config.smtp.port = request.session['smtp_port']
            return config

    def __str__(self):
        return '{}, {}'.format(
            str(self.imap),
            str(self.smtp),
            )


class _ImapConfig:  # pylint: disable=too-few-public-methods
    def __init__(self):
        self.user = None
        self.password = None
        self.host = None
        self.port = 993

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
        self.port = 465

    @property
    def is_ok(self):
        # return all(self.user, self.password)
        return True

    def __str__(self):
        return str(self.user)
