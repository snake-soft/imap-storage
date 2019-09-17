"""unittests of the imap library (not using Django tests)"""
from unittest import TestCase
from os import path
from datetime import datetime
from email import message_from_string
from . import AccountFactory, Config
from .storage.head import Head
from .storage.body import Body
from .storage.vdir import Vdir
from .storage.email import Email
from .storage.file import _File, file_from_local

__all__ = ['CustomTestCase']
TAG = 'DjangoTest'


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

        self.subject = f'{TAG} /home/TestDir/'
        self.vdir = self.account.storage.new_vdir(self.subject)
        self.email = self.vdir.emails[-1]

    def tearDown(self):
        vdirs = self.account.storage.vdirs
        vdirs = [vdir for vdir in vdirs if vdir.meta.item == 'TestDir']
        for vdir in vdirs:
            self.assertTrue(vdir.delete())
        self.assertTrue(self.account.close())


class ConfigTest(CustomTestCase):
    def test_str(self):
        config_str = f'{str(self.config.imap)}, {str(self.config.smtp)}'
        self.assertEqual(str(self.config), config_str)

    def test_is_ok(self):
        self.assertTrue(self.config.is_ok)


class StorageTest(CustomTestCase):
    def test_vdir_by_subject(self):
        self.assertIsInstance(
            self.account.storage.vdir_by_subject(self.subject),
            Vdir,
            )

    def test_email_by_uid(self):
        self.assertIsInstance(
            self.account.storage.email_by_uid(self.email.uid),
            Email,
            )


class ImapTest(CustomTestCase):
    def setUp(self):
        CustomTestCase.setUp(self)
        self.imap = self.account.imap

    def test_get_all_subjects(self):
        self.assertIsInstance(self.imap.get_all_subjects(), dict)
        self.assertIn(self.vdir.meta.subject, self.imap.get_all_subjects())

    def test_uids(self):
        self.assertIsInstance(self.imap.uids, list)
        self.assertIn(self.email.uid, self.imap.uids)

    def test_get_heads(self):
        self.assertIsInstance(self.imap.get_heads(self.imap.uids), dict)
        self.assertIsInstance(self.imap.get_heads(self.imap.uids[0]), dict)

    def test_get_bodies(self):
        self.assertIsInstance(self.imap.get_bodies(self.imap.uids), dict)
        self.assertIsInstance(self.imap.get_bodies(self.imap.uids[0]), dict)

    def test_get_file_payloads(self):
        self.assertIsInstance(
            self.imap.get_file_payloads(self.imap.uids), dict
            )
        self.assertIsInstance(
            self.imap.get_file_payloads(self.imap.uids[0]), dict
            )


class BodyTest(CustomTestCase):
    def test_add_and_remove_item(self):
        item_parent = self.email.body.add_item(
            'TEST', text='Foo', attribs={'foo': 'bar'}
            )
        self.email.body.add_item('TEST_CHILD', parent=item_parent)
        self.assertTrue(self.email.save())
        self.assertIn('<TEST foo="bar"', str(self.email.body))

        self.email.body.remove_item(item_parent.attrib['id'])
        self.assertTrue(self.email.save())
        self.assertNotIn('TEST', str(self.email.body))

        self.assertIsInstance(self.email.body.get_by_tag('container'), list)

    def test_html(self):
        self.assertTrue(self.email.html.startswith(
            'Content-Type: multipart/mixed; boundary=')
        )


class HeadTest(CustomTestCase):
    def test_from_msg_obj(self):
        msg_obj = message_from_string(self.email.plain)
        self.assertIsInstance(Head(msg_obj), Head)

        head = Head(self.email.plain)
        self.assertIsInstance(head, Head)


class EmailTest(CustomTestCase):
    def test_head(self):
        self.assertIsInstance(self.email.head, Head)
        self.email._head = None  # pylint: disable=W0212
        self.assertIsInstance(self.email.head, Head)

    def test_body(self):
        self.assertIsInstance(self.email.body, Body)

        body = str(self.email.body)
        self.email.body = body
        self.assertIsInstance(self.email.body, Body)

        self.email.body = Body(None)
        self.assertIsInstance(self.email.body, Body)

        self.email._body = None  # pylint: disable=W0212
        self.assertIsInstance(self.email.body, Body)


class VdirTest(CustomTestCase):
    def test_files(self):
        self.assertIsInstance(self.vdir.files, list)


class FileTest(CustomTestCase):
    def test_file_from_path(self):
        filepath = path.join(path.dirname(__file__), 'testfiles/textfile.txt')
        file = file_from_local(filepath)

        self.email.add_file(file)
        self.email.save()
        self.assertIsInstance(self.email.files[0], _File)
        self.assertIsInstance(self.email.xml_files[0], _File)

        for file in self.email.files:
            self.email.remove_file(file)
        self.email.save()
        self.assertEqual(len(self.email.files), 0)

        self.assertTrue(len(file.hsize))
        self.assertFalse(file.is_binary)
        self.assertIsInstance(file.htime, datetime)

        file2 = file_from_local(filepath)
        self.assertTrue(file == file2)
        self.assertFalse(file != file2)
