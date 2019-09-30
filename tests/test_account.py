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
        self.assertTrue(account3.is_ok)
        self.assertIsInstance(self.account.__repr__(), str)
        self.assertTrue(self.account.is_ok)

    def test_config(self):
        """tests of Config class"""
        self.assertTrue(self.config.is_ok)
        self.assertIsInstance(str(self.config), str)

        from types import SimpleNamespace
        session = {
            'imap_user': self.config.imap.user,
            'imap_password': self.config.imap.password,
            'imap_host': self.config.imap.host,
            'imap_port': self.config.imap.port,
            'smtp_host': self.config.imap.host,
            'smtp_port': self.config.imap.port,
            }
        request = SimpleNamespace(session=session)
        config = imap_storage.Config.from_request(request)
        self.assertTrue(config.is_ok)

        request2 = SimpleNamespace(session={})
        config2 = imap_storage.Config.from_request(request2)
        self.assertIsNone(config2)
