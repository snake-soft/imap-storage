"""test Account, AccountManager and Config classes"""
from . import CustomTestCase, imap_storage


class AccountTestCase(CustomTestCase):
    """test Account, AccountManager and Config classes"""
    def test_account_manager(self):
        """test the AccountManager"""
        accounts = imap_storage.AccountManager()
        account2 = accounts.new(self.config, 1)
        self.assertEqual(self.account, account2)
        self.assertFalse(self.account != account2)
        self.assertFalse(self.account < account2)
        account2.close()

        account3 = accounts.by_id(1)
        self.assertFalse(account3.is_ok())  # has not all data
        self.assertIsInstance(self.account.__repr__(), str)
        self.assertTrue(self.account.is_ok()) # has all needed data
