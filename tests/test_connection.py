"""test connection.* classes"""
from . import CustomTestCase, imap_storage


class ConnectionTestCase(CustomTestCase):
    """test connection.* classes"""
    def test_imap(self):
        """test connection.Imap class"""
        self.create_test_email()
        imap = self.account.imap
        self.assertIsInstance(imap.get_all_subjects(), dict)
        self.assertRaises(AttributeError, lambda: imap.fetch([], ''))
        self.assertIsInstance(
            imap.get_all_subjects(self.config.directory), dict
            )

    def test_unsafe_account(self):
        """test login with unsafe ssl configuration"""
        account = imap_storage.Account(self.config, 2, unsafe=True)
        self.assertEqual(account.imap.state, 'SELECTED')
        account.close()

