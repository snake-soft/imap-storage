"""test connection.* classes"""
from . import CustomTestCase, imap_storage


class ConnectionTestCase(CustomTestCase):
    """test connection.* classes"""
    def test_imap(self):
        """test connection.Imap class"""
        self.create_test_email()
        imap = self.account.imap
        storage = self.account.storage
        self.assertIsInstance(storage.get_subjects(), dict)
        self.assertRaises(AttributeError, lambda: imap.fetch([], ''))
        self.assertIsInstance(
            storage.get_subjects(self.config.directory), dict
            )
        self.assertEqual(imap.clean_folder_path(''), imap.config.directory)
        self.assertFalse(imap.create_folder(imap.config.directory))
        self.assertFalse(imap.select_folder('_SHOULNTEXIST'))
        self.assertEqual(self.config.imap.user, str(imap))

    def test_unsafe_account(self):
        """test login with unsafe ssl configuration"""
        account = imap_storage.Account(self.config, 2, unsafe=True)
        self.assertEqual(account.imap.state, 'SELECTED')
        account.close()

    def test_delete_folder(self):
        imap = self.account.imap
        self.assertEqual(imap.delete_folder(self.config.directory), [])
        self.assertTrue(imap.create_folder('bla'))
        self.assertIn(self.config.directory + '.bla', imap.list_folders())
        self.assertTrue(imap.delete_folder('bla'))
        self.assertNotIn(self.config.directory + '.bla', imap.list_folders())
        # *** imapclient.exceptions.LoginError: Unable to connect

    def test_delete_messages(self):
        imap = self.account.imap
        email = self.create_test_email()
        self.assertIn(email.uid, imap.search())
        imap.delete_messages(float(email.uid))
        self.assertNotIn(email.uid, imap.search())

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
