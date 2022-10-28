from unittest import TestCase
from unittest.mock import patch, MagicMock

from boxman.args_parser import parse_args, get_mode_from_args
from boxman.data.mode import Mode


class TestArgparser(TestCase):
    def test_install(self):
        actual = parse_args(["install", "test"])
        self.assertEqual(["test"], actual.arguments)
        self.assertEqual(Mode.INSTALL, actual.mode)

    def test_install_multiple_packages(self):
        actual = parse_args(["install", "test1", "test2"])
        self.assertEqual(["test1", "test2"], actual.arguments)
        self.assertEqual(Mode.INSTALL, actual.mode)

    @patch("sys.exit")
    def test_install_no_packages(self, mock_exit: MagicMock):
        parse_args(["install"])
        mock_exit.assert_called_with(2)

    def test_list(self):
        actual = parse_args(["list"])
        self.assertEqual(None, actual.arguments)
        self.assertEqual(Mode.LIST, actual.mode)

    def test_search(self):
        actual = parse_args(["search", "test"])
        self.assertEqual(["test"], actual.arguments)
        self.assertEqual(Mode.SEARCH, actual.mode)

    @patch("sys.exit")
    def test_search_multiple(self, mock_exit: MagicMock):
        parse_args(["search", "test1", "test2"])
        mock_exit.assert_called_with(2)

    @patch("sys.exit")
    def test_search_no_string(self, mock_exit: MagicMock):
        parse_args(["search"])
        mock_exit.assert_called_with(2)

    def test_installed(self):
        actual = parse_args(["installed"])
        self.assertEqual(None, actual.arguments)
        self.assertEqual(Mode.INSTALLED, actual.mode)

    def test_remove(self):
        actual = parse_args(["remove", "test"])
        self.assertEqual(["test"], actual.arguments)
        self.assertEqual(Mode.REMOVE, actual.mode)

    def test_remove_multiple_packages(self):
        actual = parse_args(["remove", "test1", "test2"])
        self.assertEqual(["test1", "test2"], actual.arguments)
        self.assertEqual(Mode.REMOVE, actual.mode)

    @patch("sys.exit")
    def test_remove_no_packages(self, mock_exit: MagicMock):
        parse_args(["remove"])
        mock_exit.assert_called_with(2)

    def test_show(self):
        actual = parse_args(["show", "test"])
        self.assertEqual(["test"], actual.arguments)
        self.assertEqual(Mode.SHOW, actual.mode)

    @patch("sys.exit")
    def test_show_multiple_packages(self, mock_exit: MagicMock):
        parse_args(["show", "test1", "test2"])
        mock_exit.assert_called_with(2)

    def test_show_no_packages(self):
        actual = parse_args(["show"])
        self.assertEqual([""], actual.arguments)
        self.assertEqual(Mode.SHOW, actual.mode)

    def test_update(self):
        actual = parse_args(["update"])
        self.assertEqual([], actual.arguments)
        self.assertEqual(Mode.UPDATE, actual.mode)

    def test_update_one_package(self):
        actual = parse_args(["update", "test"])
        self.assertEqual(["test"], actual.arguments)
        self.assertEqual(Mode.UPDATE, actual.mode)

    def test_update_multiple_packages(self):
        actual = parse_args(["update", "test1", "test2"])
        self.assertEqual(["test1", "test2"], actual.arguments)
        self.assertEqual(Mode.UPDATE, actual.mode)

    @patch("sys.exit")
    def test_no_mode_set(self, mock_exit: MagicMock):
        parse_args([])
        mock_exit.assert_called_with(2)

    def test_get_mode_from_args_no_mode(self):
        args = MagicMock()
        args.mode = None
        mode = get_mode_from_args(args)
        self.assertEqual(Mode.NOT_SET, mode)
