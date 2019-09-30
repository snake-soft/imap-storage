"""
This test module tests all examples that are documented
These tests should not include some predefined test cases to have
a reasonable result.
"""
from unittest import TestCase
from imap_storage import Account, Config
from tests import USER, PASSWORD, HOST, PORT


class ReadmeQuickstartTestcase(TestCase):
    """this is the test for the example that is written in README.md"""
    def test_example_readme_quickstart(self):
        """run test"""
        config = Config()
        config.imap.user = USER
        config.imap.password = PASSWORD
        config.imap.host = HOST
        config.imap.port = PORT

        account = Account(config, 1)
        self.assertTrue(account.imap.is_ok)
        directory = account.storage.directory_by_path(account.config.directory)
        email = directory.new_email('Your_first_item')
        email.add_item('TestMessage', text='Your first message')
        email.save()
        self.assertIsInstance(email.uid, int)
        self.assertIn(email, directory.emails)
        email.delete()
        self.assertNotIn(email, directory.emails)
        account.close()
        self.assertFalse(account.imap.is_ok)
