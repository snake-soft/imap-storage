from copy import copy
from os import path
from datetime import datetime
from . import CustomTestCase
from imap_storage.storage.email.head import Head
from imap_storage.storage.email.body import Body
from imap_storage.storage.email.file import file_from_local, _File


class EmailTestCase(CustomTestCase):  # imap.py", line 64, in connect
    """test storage.email.* classes"""
    def test_created_email(self):
        """test created testmail"""
        email = self.create_test_email()
        self.assertIsInstance(email.head, Head)
        self.assertIsInstance(email.body, Body)

    def test_email(self):
        """test storage.email.Email class"""
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
        """test storage.email.Body class"""
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
        """test storage.email.Head class"""
        email = self.create_test_email()
        self.assertIsInstance(email.head, Head)
        email.head = self.email.plain
        self.assertIsInstance(email.head, Head)

    def test_files(self):
        """test storage.email.Files class"""
        email = self.create_test_email()

        filepath = path.join(path.dirname(__file__), 'files/text.txt')
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
