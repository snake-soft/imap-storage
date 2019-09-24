"""unittests of the imap library (not using Django tests)"""
from unittest import TestCase, main
import sys
from os import path
from copy import copy
from datetime import datetime
from imap_storage import AccountManager, Account, Config
from imap_storage.storage.directory import Directory
from imap_storage.storage.email.head import Head
from imap_storage.storage.email.body import Body
from imap_storage.storage.email.file import file_from_local, _File
from tests.secrets import USER, PASSWORD, HOST, PORT
print(sys.version)


class CustomTestCase(TestCase):
    def setUp(self):
        config = Config()
        config.imap.user = USER
        config.imap.password = PASSWORD
        config.imap.host = HOST
        config.imap.port = PORT
        config.tag = 'PythonUnittest'
        config.directory = 'chat'
        self.config = config
        self.account = Account(config, 1)
        self.email = None

    def create_test_email(self):
        self.account.imap.select_folder_or_create(self.config.directory)
        directory = self.account.storage.directory_by_path(
            self.config.directory
            )
        self.email = directory.new_email('Testobject')
        self.email.save()
        return self.email

    def tearDown(self):
        self.account.close()
        if self.email:
            self.email.delete()


class AccountTestCase(CustomTestCase):
    def test_account_manager(self):
        accounts = AccountManager()
        account2 = accounts.new(self.config, 1)
        self.assertEqual(self.account, account2)
        self.assertFalse(self.account != account2)
        self.assertFalse(self.account < account2)
        account2.close()

        account3 = accounts.by_id(1)
        self.assertTrue(account3.is_ok)
        self.assertIsInstance(self.account.__repr__(), str)

    def test_is_ok(self):
        self.assertTrue(self.account.is_ok)

    def test_config(self):
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
        config = Config.from_request(request)
        self.assertTrue(config.is_ok)

        request2 = SimpleNamespace(session={})
        config2 = Config.from_request(request2)
        self.assertIsNone(config2)

    def test_unsafe_account(self):
        account = Account(self.config, 2, unsafe=True)
        self.assertEqual(account.imap.state, 'SELECTED')
        account.close()

class ConnectionTestCase(CustomTestCase):
    def test_imap(self):
        self.create_test_email()
        imap = self.account.imap
        self.assertIsInstance(imap.get_all_subjects(), dict)
        self.assertRaises(AttributeError, lambda: imap.fetch([], ''))
        self.assertIsInstance(imap.get_all_subjects(self.config.directory), dict)


class StorageTestCase(CustomTestCase):
    def test_storage(self):
        storage = self.account.storage
        self.assertIsInstance(storage.directories, list)
        self.assertIsNone(storage.directory_by_path('XYZ'))
        new_dir_path = 'abc.def'
        self.assertIsInstance(
            storage.new_directory(new_dir_path),
            Directory
            )
        self.assertIsInstance(
            storage.new_directory(new_dir_path),
            Directory
            )  # yes, two times
        self.assertIsInstance(
            storage.directory_by_path(new_dir_path),
            Directory
            )
        self.assertTrue(storage.delete_directory(new_dir_path))
        self.assertFalse(storage.delete_directory(new_dir_path))

        test_path = self.config.directory + '.xyz_test.path'
        storage.new_directory(test_path)
        self.assertIsInstance(storage.directory_by_path(test_path), Directory)
        self.assertTrue(storage.delete_directory(test_path))
        self.assertIsNone(storage.directory_by_path(test_path))


class DirectoryTestCase(CustomTestCase):
    def test_directory(self):
        storage = self.account.storage
        directory = storage.directory_by_path(
            self.config.directory
            )
        self.assertEqual(directory.appname, self.config.directory)
        self.assertIsInstance(directory.uids, list)
        self.assertIsInstance(directory.emails, list)
        self.assertIsInstance(hash(directory), int)

        directory2 = copy(directory)
        self.assertIsNot(directory, directory2)
        self.assertEqual(directory, directory2)
        self.assertTrue(directory == directory2)
        self.assertFalse(directory != directory2)
        self.assertIsInstance(directory.__repr__(), str)
        self.assertIsInstance(str(directory), str)

class EmailTestCase(CustomTestCase):
    def test_created_email(self):
        email = self.create_test_email()
        self.assertIsInstance(email.head, Head)
        self.assertIsInstance(email.body, Body)

    def test_email(self):
        self.create_test_email()
        directory = self.account.storage.directory_by_path(
            self.config.directory
            )
        email = directory.emails[0]
        self.assertIsInstance(email.head, Head)
        self.assertIsInstance(email.body, Body)
        self.assertIsInstance(email.html, str)
        self.assertIsInstance(email.__repr__(), str)
        self.assertTrue(directory.delete_email(email.uid))
        self.assertIsInstance(hash(email), int)
        self.assertIsInstance(email.__repr__(), str)

        email2 = copy(email)
        self.assertIsNot(email, email2)
        self.assertEqual(email, email2)
        self.assertTrue(email == email2)
        self.assertFalse(email != email2)
        self.assertFalse(email < email2)
        self.assertIsInstance(email.__repr__(), str)

    def test_body(self):
        email = self.create_test_email()
        email.add_item('message', attribs={'creator': 'test'})
        self.assertIs(len(email.body.get_by_tag('message')), 1)
        parent = email.body.get_by_tag('message')[0]
        email.add_item('bla', text='Hallo', parent=parent)
        email.save()
        email.body.remove_item(parent.attrib['id'])
        email.save()
        self.assertIs(len(email.body.get_by_tag('message')), 0)

    def test_head(self):
        email = self.create_test_email()
        self.assertIsInstance(email.head, Head)
        email.head = self.email.plain
        self.assertIsInstance(email.head, Head)

    def test_files(self):
        email = self.create_test_email()

        filepath = path.join(path.dirname(__file__), 'tests/testfile.txt')
        file = file_from_local(filepath)
        file.mime = None

        email.add_file(file)
        email.save()
        self.assertIsInstance(email.files[0], _File)
        self.assertIsInstance(email.xml_files[0], _File)

        for file in self.email.files:
            email.remove_file(file)
        email.save()
        self.assertEqual(len(email.files), 0)

        self.assertTrue(len(file.hsize))
        self.assertFalse(file.is_binary)
        self.assertIsInstance(file.htime, datetime)

        file2 = file_from_local(filepath)
        self.assertTrue(file == file2)
        self.assertFalse(file != file2)
        self.assertEqual(file.human_readable_size(10), '10.0B')
        self.assertEqual(file.human_readable_size(1024*1024), '1.0MiB')
        self.assertEqual(file.human_readable_size(2**80), '1.0YiB')

        file3 = file_from_local(
            path.join(path.dirname(__file__), 'tests/testfile.mp3')
            )
        email.add_file(file3)
        file4 = file_from_local(
            path.join(path.dirname(__file__), 'tests/testfile.png')
            )
        email.add_file(file4)
        file5 = file_from_local(
            path.join(path.dirname(__file__), 'tests/testfile')
            )
        file5.mime = None
        email.add_file(file5)
        self.assertTrue(file3 < file4)
        self.assertIsInstance(str(file5), str)
        self.assertIsInstance(email.plain, str)
        self.assertIsInstance(email.file_by_id(file5.id_), _File)
        self.assertIsInstance(email.file_by_name('testfile'), _File)


if __name__ == '__main__':
    main()
