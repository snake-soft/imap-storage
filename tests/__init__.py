from unittest import TestCase
from os import environ
import imap_storage
from uuid import uuid4 as uuid

NEEDED_ENV_VARS = (
    'IMAP_STORAGE_USER',
    'IMAP_STORAGE_PASSWORD',
    'IMAP_STORAGE_HOST'
    )
for var in NEEDED_ENV_VARS:
    if var not in environ:
        raise(AttributeError(
            var + 'not found as environment variable. \
            Look at /environment.sample.sh'
            ))
USER = environ.get('IMAP_STORAGE_USER')
PASSWORD = environ.get('IMAP_STORAGE_PASSWORD')
HOST = environ.get('IMAP_STORAGE_HOST')
PORT = environ.get('IMAP_STORAGE_PORT', 993)


class CustomTestCase(TestCase):
    """Class of all test cases"""
    def setUp(self):
        config = imap_storage.Config()
        config.imap.user = USER
        config.imap.password = PASSWORD
        config.imap.host = HOST
        config.imap.port = PORT
        config.tag = 'PythonUnittest'
        config.directory = 'imap_storage_tests_' + str(uuid())
        self.config = config
        self.account = imap_storage.Account(config, 1)
        self.email = None
        self.directory = self.account.storage.directory_by_path(
            self.config.directory
            )

    def create_test_email(self):
        """create the test email
        :returns: new self.email (Email object)
        """
        self.account.imap.create_folder(self.config.directory)
        self.email = self.directory.new_email('Testobject')
        self.email.save()
        return self.email

    def tearDown(self):
        for email in self.directory.emails:
            email.delete()
        for directory in self.directory.childs:
            directory.delete()
        self.account.storage.uninstall()
        self.account.close()
