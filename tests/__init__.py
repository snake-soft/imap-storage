from unittest import TestCase
import imap_storage
try:
    from tests.secrets import USER, PASSWORD, HOST, PORT
except ModuleNotFoundError:
    raise(AttributeError(
        'No /tests/secrets.py found. Use /tests/secrets.sample.py'
        ))


class CustomTestCase(TestCase):
    """Class of all test cases"""
    def setUp(self):
        config = imap_storage.Config()
        config.imap.user = USER
        config.imap.password = PASSWORD
        config.imap.host = HOST
        config.imap.port = PORT
        config.tag = 'PythonUnittest'
        config.directory = 'chat'
        self.config = config
        self.account = imap_storage.Account(config, 1)
        self.email = None

    def create_test_email(self):
        """create the test email
        :returns: new self.email (Email object)
        """
        self.account.imap.select_folder_or_create(self.config.directory)
        directory = self.account.storage.directory_by_path(
            self.config.directory
            )
        self.email = directory.new_email('Testobject')
        self.email.save()
        return self.email

    def tearDown(self):
        if self.email:
            self.email.delete()
        self.account.close()
