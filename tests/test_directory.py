"""test storage.directory class"""
from . import CustomTestCase
from imap_storage.storage.directory import Directory
from imap_storage.storage.email.file import file_from_local
from email.message import Message

class ConnectionTestCase(CustomTestCase):
    """test storage.directory class"""
    def test_directory(self):
        """test storage.directory class"""
        imapdir = self.account.config.directory
        storage = self.account.storage
        directories = storage.directories
        self.assertIn(imapdir, [directory.path for directory in directories])
        parent_dir = storage.directory_by_path(imapdir)
        child_dir = storage.new_directory(imapdir + '.child')
        self.assertIsNone(parent_dir.parent)
        self.assertIsInstance(child_dir.parent, Directory)
        self.assertIsInstance(parent_dir.childs, list)
        self.assertFalse(' ' in Directory(storage, ' fdsa ').folder)
        self.assertIs(child_dir.breadcrumbs[0], parent_dir)
        self.assertEqual(parent_dir.item_name, parent_dir.app_name)

        parent_dir.path = ''
        self.assertEqual(parent_dir.url, '')
        self.assertEqual(child_dir.url, 'child')

        #email = self.create_test_email()
        email = parent_dir.new_email('Testobject')
        email.save()

        self.assertEqual(parent_dir.email_by_uid(email.uid), email)
        email.delete()

        file = file_from_local('tests/files/text.txt')
        file_email = parent_dir.add_file_email(file)
        self.assertIn(file, parent_dir.files)

        self.assertIsInstance(parent_dir.fetch_subjects(), dict)
        self.assertIsInstance(parent_dir.fetch_subjects(file_email), dict)
        self.assertIsInstance(parent_dir.fetch_head(file_email), str)
        self.assertIsInstance(parent_dir.fetch_body(file_email), str)
        self.assertIsInstance(
            parent_dir.fetch_payloads(file_email)[0], Message
            )
        self.assertIsInstance(hash(parent_dir), int)

        self.assertIn(file_email, parent_dir.emails)
        parent_dir.delete_email(file_email)
        self.assertNotIn(file_email, parent_dir.emails)

    def test_email_deletion(self):
        imapdir = self.account.config.directory
        storage = self.account.storage
        parent_dir = storage.directory_by_path(imapdir)
        child_dir = storage.new_directory(imapdir + '.child')
        email = self.create_test_email()
        self.assertEqual(
            [email.uid for email in parent_dir.emails], parent_dir.uids
            )
        self.assertIn(email, parent_dir.emails)
        parent_dir.delete_email(email.uid)
        self.assertNotIn(email, parent_dir.emails)

        email2 = self.create_test_email()
        self.assertTrue(parent_dir != child_dir)
        self.assertIsInstance(child_dir.__repr__(), str)
        self.assertIsInstance(str(child_dir), str)
        self.assertIn(email2, parent_dir.emails)
        email2.delete()
        self.assertNotIn(email2, parent_dir.emails)
        child_dir.delete()
        # self.assertNotIn(child_dir, storage.directories)
