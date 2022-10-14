from unittest import TestCase
from unittest.mock import mock_open, patch, MagicMock

from boxman import Config


class TestConfig(TestCase):
    def test_init(self):
        data = (
            "[options]\n"
            "RootDir = /psp\n"
            "CacheDir = /cache/dir\n"
            "DBPath=/db/path\n"
            "\n"
            "[minigalaxy]\n"
            "Server = https://github.com/sharkwouter/arch-repo-test/releases/latest/download\n"
            "[some_other_repo]\n"
            "Server = https://some/repo"
        )
        with patch("builtins.open", mock_open(read_data=data)):
            config = Config("/base/dir")

        self.assertEqual("/base/dir", config.base_directory)
        self.assertEqual("/base/dir/cache/dir", config.options.cache_dir)
        self.assertEqual("/base/dir/db/path", config.options.db_path)
        self.assertEqual("/base/dir/psp", config.options.root_dir)
        self.assertEqual(2, len(config.repositories))

        self.assertEqual("minigalaxy", config.repositories[0].name)
        self.assertEqual(
            "https://github.com/sharkwouter/arch-repo-test/releases/latest/download",
            config.repositories[0].server,
        )
        self.assertEqual("some_other_repo", config.repositories[1].name)
        self.assertEqual("https://some/repo", config.repositories[1].server)

    def test_init2(self):
        data = (
            "[options]\n"
            "RootDir = psp\n"
            "CacheDir = cache/dir\n"
            "DBPath=db/path\n"
            "\n"
            "[minigalaxy]\n"
            "Server = https://github.com/sharkwouter/arch-repo-test/releases/latest/download\n"
        )
        with patch("builtins.open", mock_open(read_data=data)):
            config = Config("/base/dir")

        self.assertEqual("/base/dir", config.base_directory)
        self.assertEqual("/base/dir/cache/dir", config.options.cache_dir)
        self.assertEqual("/base/dir/db/path", config.options.db_path)
        self.assertEqual("/base/dir/psp", config.options.root_dir)
        self.assertEqual(1, len(config.repositories))

        self.assertEqual("minigalaxy", config.repositories[0].name)
        self.assertEqual(
            "https://github.com/sharkwouter/arch-repo-test/releases/latest/download",
            config.repositories[0].server,
        )

    def test_init_defaults(self):
        with patch("builtins.open", mock_open(read_data="")):
            config = Config("/base/dir")

        self.assertEqual("/base/dir", config.base_directory)
        self.assertEqual("/base/dir/var/cache/boxman/pkg", config.options.cache_dir)
        self.assertEqual("/base/dir/var/lib/boxman", config.options.db_path)
        self.assertEqual("/base/dir", config.options.root_dir)
        self.assertEqual(0, len(config.repositories))

    def test_get_relative_path(self):
        with patch("builtins.open", mock_open(read_data="")):
            config = Config("/base/dir")

        self.assertEqual("/base/dir/", config.get_relative_path("/"))
        self.assertEqual("/base/dir/root/.ssh", config.get_relative_path("/root/.ssh"))
        self.assertEqual("/base/dir/", config.get_relative_path("/../../.."))
        self.assertEqual("/base/dir/root", config.get_relative_path("//////root"))
        self.assertEqual("/base/dir/root", config.get_relative_path("/../../../root"))
        self.assertEqual("/base/dir/root", config.get_relative_path("root"))

    @patch("sys.platform", new="win32")
    @patch("os.path.join")
    def test_get_relative_path_windows(self, mock_join: MagicMock):
        with patch("builtins.open", mock_open(read_data="")):
            config = Config("C:\\root")

        config.get_relative_path("E:\\Program Files\\")
        mock_join.assert_called_with("C:\\root", "Program Files\\")

        config.get_relative_path("..\\Program Files\\")
        mock_join.assert_called_with("C:\\root", "Program Files\\")

        config.get_relative_path("/root")
        mock_join.assert_called_with("C:\\root", "root")

        config.get_relative_path("\\root")
        mock_join.assert_called_with("C:\\root", "root")

        config.get_relative_path("root")
        mock_join.assert_called_with("C:\\root", "root")

        config.get_relative_path("..\\..\\..\\root")
        mock_join.assert_called_with("C:\\root", "root")
