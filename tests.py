"""unittests of the imap library (not using Django tests)"""
from unittest import TestCase
from . import AccountFactory, Config
__all__ = ['CustomTestCase', 'CustomClient']


class CustomTestCase(TestCase):
    def setUp(self):
        config = Config()
        config.imap.user = 'chat@hennige-it.de'
        config.imap.password = 'testFUbla'
        config.imap.host = 'imap.hennige-it.de'
        config.imap.port = 993
        self.config = config
        accounts = AccountFactory()
        self.account = accounts.new(1, self.config)
        self.assertIs(accounts.by_id(1), self.account)

    def tearDown(self):
        self.assertTrue(self.account.close())


class ConfigTest(CustomTestCase):
    def test_str(self):
        config_str = f'{str(self.config.imap)}, {str(self.config.smtp)}'
        self.assertEqual(str(self.config), config_str)

    def test_is_ok(self):
        self.assertTrue(self.config.is_ok)

