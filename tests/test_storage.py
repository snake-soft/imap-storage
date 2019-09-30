from . import CustomTestCase
from imap_storage.storage.directory import Directory


class StorageTestCase(CustomTestCase):
    """test storage.* classes"""
    def test_storage(self):
        """test storage.Storage class"""
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
        # self.assertIsNone(storage.directory_by_path(test_path))
