"""unittests of the imap library (not using Django tests)"""
from unittest import TestCase, main
import sys
#sys.path.append('../imap_storage')
#import pdb; pdb.set_trace()  # <---------
from imap_storage import AccountManager, Account, Config
#from pathlib import Path
import sys
print(sys.version)

class CustomTestCase(TestCase):
    def setUp(self):
        config = Config()
        config.imap.user = 'chat@hennige-it.de'
        config.imap.password = 'testFUbla'
        config.imap.host = 'imap.hennige-it.de'
        config.imap.port = 993
        config.tag = 'PythonUnittest'
        self.config = config
        self.account = Account(config, 1)

    def tearDown(self):
        self.account.close()


class AccountTestCase(CustomTestCase):
    def test_account(self):
        accounts = AccountManager()
        account2 = accounts.new(self.config, 1)
        self.assertEqual(self.account, account2)
        account2.close()

    def test_is_ok(self):
        self.assertTrue(self.account.is_ok)

class ConnectionTestCase(CustomTestCase):
    def test_imap(self):
        pass


class StorageTestCase(CustomTestCase):
    pass


class DirectoryTestCase(CustomTestCase):
    pass


class EmailTestCase(CustomTestCase):
    pass


if __name__ == '__main__':
    main()
