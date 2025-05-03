import unittest
import os
from unittest.mock import patch, MagicMock, PropertyMock
from tree import Tree, NormalTree, OakTree, TreeFactory

TEST_BASE_PATH_WITH_IMAGES = "C:/Users/Ruslan/Desktop/BOTAS" # <--- PAKEISKITE Į SAVO KELIĄ!

class TestTreeClasses(unittest.TestCase):

    def test_normal_tree_level(self):
        original_path = TreeFactory.base_path
        TreeFactory.base_path = TEST_BASE_PATH_WITH_IMAGES
        if not os.path.exists(TEST_BASE_PATH_WITH_IMAGES):
             self.skipTest(f"Testavimo paveikslėlių katalogas nerastas: {TEST_BASE_PATH_WITH_IMAGES}")

        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            tree = TreeFactory.create_tree("normal")
            self.assertIsInstance(tree, NormalTree)
            self.assertEqual(tree.required_level(), 1)
            self.assertEqual(tree.name, "Normal Tree")
            self.assertIsInstance(tree.image_paths, list)
            self.assertTrue(any(TEST_BASE_PATH_WITH_IMAGES in path for path in tree.image_paths))
        TreeFactory.base_path = original_path

    def test_oak_tree_level(self):
        original_path = TreeFactory.base_path
        TreeFactory.base_path = TEST_BASE_PATH_WITH_IMAGES
        if not os.path.exists(TEST_BASE_PATH_WITH_IMAGES):
            self.skipTest(f"Testavimo paveikslėlių katalogas nerastas: {TEST_BASE_PATH_WITH_IMAGES}")

        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            tree = TreeFactory.create_tree("oak")
            self.assertIsInstance(tree, OakTree)
            self.assertEqual(tree.required_level(), 15)
            self.assertEqual(tree.name, "Oak Tree")
            self.assertIsInstance(tree.image_paths, list)
            self.assertTrue(any(TEST_BASE_PATH_WITH_IMAGES in path for path in tree.image_paths))
        TreeFactory.base_path = original_path

class TestTreeFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original_base_path = TreeFactory.base_path
        TreeFactory.base_path = TEST_BASE_PATH_WITH_IMAGES

        cls.test_dir = "temp_test_tree_files"
        os.makedirs(cls.test_dir, exist_ok=True)
        cls.dummy_files = ["tree.png", "oak.png", "some_other_file.txt"]
        for fname in cls.dummy_files:
            with open(os.path.join(cls.test_dir, fname), "w") as f:
                f.write("dummy")

    @classmethod
    def tearDownClass(cls):
        TreeFactory.base_path = cls.original_base_path
        for fname in cls.dummy_files:
             try:
                 os.remove(os.path.join(cls.test_dir, fname))
             except OSError:
                 pass
        try:
            os.rmdir(cls.test_dir)
        except OSError:
            pass

    def setUp(self):
        TreeFactory.base_path = TEST_BASE_PATH_WITH_IMAGES
        if not os.path.exists(TEST_BASE_PATH_WITH_IMAGES):
             self.skipTest(f"Testavimo paveikslėlių katalogas nerastas: {TEST_BASE_PATH_WITH_IMAGES}")


    @patch('os.path.exists')
    def test_create_tree_success(self, mock_exists):
        mock_exists.return_value = True
        normal_tree = TreeFactory.create_tree("normal")
        self.assertIsInstance(normal_tree, NormalTree)
        oak_tree = TreeFactory.create_tree("oak")
        self.assertIsInstance(oak_tree, OakTree)

    @patch('os.path.exists')
    def test_create_tree_base_path_not_found(self, mock_exists):
        mock_exists.side_effect = [False, True, True]
        with self.assertRaisesRegex(FileNotFoundError, "Bazinis kelias nerastas"):
            TreeFactory.create_tree("normal")
        mock_exists.assert_any_call(TEST_BASE_PATH_WITH_IMAGES)


    @patch('os.path.exists')
    def test_create_tree_image_file_not_found(self, mock_exists):
        required_paths = [os.path.join(TEST_BASE_PATH_WITH_IMAGES, f) for f in [
            "tree.png", "tree_v1.png", "tree_v2.png", "tree_v3.png", "tree_v4.png", "tree_v5.png"
        ]]
        exists_results = [True] + [True, True, False, True, True, True]
        mock_exists.side_effect = exists_results

        with self.assertRaisesRegex(FileNotFoundError, "Trūksta vieno ar daugiau paveikslėlių"):
            TreeFactory.create_tree("normal")

        mock_exists.assert_any_call(TEST_BASE_PATH_WITH_IMAGES)
        for path in required_paths:
             mock_exists.assert_any_call(path)

    def test_create_tree_unknown_type(self):
        with patch('os.path.exists', return_value=True):
             with self.assertRaisesRegex(ValueError, "Unknown tree type: maple"):
                TreeFactory.create_tree("maple")

    @patch('tree.TreeFactory.base_path', new_callable=PropertyMock)
    def test_check_required_files_success(self, mock_base_path):
        mock_base_path.return_value = self.test_dir
        required = ["tree.png", "oak.png"]
        try:
            TreeFactory.check_required_files(self.test_dir, required)
        except FileNotFoundError:
            self.fail("check_required_files() sukėlė FileNotFoundError, kai visi failai egzistuoja")

    @patch('tree.TreeFactory.base_path', new_callable=PropertyMock)
    def test_check_required_files_missing(self, mock_base_path):
        mock_base_path.return_value = self.test_dir
        required = ["tree.png", "missing_file.png"]
        with self.assertRaisesRegex(FileNotFoundError, "Trūksta vieno ar daugiau reikalingų paveikslėlių failų"):
             TreeFactory.check_required_files(self.test_dir, required)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)