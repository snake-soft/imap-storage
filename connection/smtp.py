from smtplib import SMTP_SSL


class Smtp(SMTP_SSL):
    """ Controls SMTP access via SSL """

    def __init__(self, config):  # host, user, pw, port=465):
        self.config = config
        self.first = False

    """ Sends Messages from_, to, email.message object
    login returns already logged in
    """

    def get_state(self):
        result = self.noop()[0]
        return result

    def first_login(self):
        """ gui thread needs that """
        SMTP_SSL.__init__(
            self,
            self.config.smtp_host,
            port=self.config.smtp_port
            )
        self.login(self.config.smtp_user, self.config.smtp_pw)

    def send_msg(self, from_, to, msg):
        if not self.first:
            self.first_login()
            self.first = True
        if self.get_state() is not 250:
            self.first_login()
        # self.login(self.user, self.pw)
        self.sendmail(from_, to, str(msg))
