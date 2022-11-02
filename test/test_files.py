from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from boxman.files import Files


class TestFiles(TestCase):
    def test_init_content(self):
        content = "%FILES%\n" "test\n" "test/test1\n" "test/test2\n"
        files = Files("/root", content)
        self.assertEqual(["test", "test/test1", "test/test2"], files._Files__files)

    def test_init_file_list(self):
        file_list = [
            "test",
            "test/test1",
            "test/test2",
        ]
        files = Files("/root", file_list=file_list)
        self.assertEqual(["test", "test/test1", "test/test2"], files._Files__files)

    def test_init_no_files_given(self):
        self.assertRaisesRegex(
            Exception,
            r"Either content of file_list has to be set",
            Files,
            "/test/var/lib/boxman/local",
        )

    @patch("os.path.isfile")
    @patch("os.path.isdir")
    @patch("os.remove")
    @patch("os.rmdir")
    def test_remove_files(
        self,
        mock_rmdir: MagicMock,
        mock_remove: MagicMock,
        mock_isdir: MagicMock,
        mock_isfile: MagicMock,
    ):
        file_list = [
            "test",
            "test/test1",
            "test/test2",
        ]
        files = Files("/home/test/root", file_list=file_list)

        mock_isfile.side_effect = [True, True, False]
        mock_isdir.return_value = True

        files.remove_files()
        mock_remove.assert_called_with("/home/test/root/test/test1")
        mock_remove.assert_has_calls([call("/home/test/root/test/test2")])

        mock_rmdir.assert_called_once_with("/home/test/root/test")

    def test_get_files(self):
        file_list = [
            "test",
            "test/test1",
            "test/test2",
        ]
        files = Files("/home/test/root", file_list=file_list)

        expected = [
            "/home/test/root/test",
            "/home/test/root/test/test1",
            "/home/test/root/test/test2",
        ]
        actual = files.get_files()

        self.assertEqual(expected, actual)

    def test_get_full_path(self):
        files = Files("/home/test/root", file_list=["test"])

        self.assertEqual(
            "/home/test/root/test",
            files.get_full_path("test"),
        )

    def test_repr(self):
        file_list = [
            "test",
            "test/test1",
            "test/test2",
        ]
        files = Files("/home/test/root", file_list=file_list)

        expected = "%FILES%\n" "test\n" "test/test1\n" "test/test2\n"
        actual = repr(files)

        self.assertEqual(expected, actual)
