import os
from unittest import TestCase
from unittest.mock import mock_open, patch, MagicMock

from boxman.config import Config


class TestConfig(TestCase):
    @patch("os.path.isfile")
    @patch("__main__.__file__", new="/base/dir/boxman")
    def test_init_full_path_root(self, mock_isfile: MagicMock):
        mock_isfile.return_value = True
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
            config = Config()

        self.assertEqual("/base/dir", config.base_directory)
        self.assertEqual("/psp/cache/dir", config.options.cache_dir)
        self.assertEqual("/psp/db/path", config.options.db_path)
        self.assertEqual("/psp", config.options.root_dir)
        self.assertEqual(2, len(config.repositories))

        self.assertEqual("minigalaxy", config.repositories[0].name)
        self.assertEqual(
            "https://github.com/sharkwouter/arch-repo-test/releases/latest/download/minigalaxy.db",
            config.repositories[0].url,
        )
        self.assertEqual("some_other_repo", config.repositories[1].name)
        self.assertEqual(
            "https://some/repo/some_other_repo.db", config.repositories[1].url
        )

    @patch("os.path.isfile")
    @patch("__main__.__file__", new="/base/dir/boxman")
    def test_init(self, mock_isfile: MagicMock):
        mock_isfile.return_value = True
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
            config = Config()

        self.assertEqual("/base/dir", config.base_directory)
        self.assertEqual("/base/dir/psp/cache/dir", config.options.cache_dir)
        self.assertEqual("/base/dir/psp/db/path", config.options.db_path)
        self.assertEqual("/base/dir/psp", config.options.root_dir)
        self.assertEqual(1, len(config.repositories))

        self.assertEqual("minigalaxy", config.repositories[0].name)
        self.assertEqual(
            "https://github.com/sharkwouter/arch-repo-test/releases/latest/download/minigalaxy.db",
            config.repositories[0].url,
        )

    @patch("os.path.isfile")
    @patch("__main__.__file__", new="/base/dir/boxman")
    def test_init_env_var_root(self, mock_isfile: MagicMock):
        mock_isfile.return_value = True
        os.environ["PSPDEV"] = "/home/test/pspdev"
        data = (
            "[options]\n"
            "RootDir = $PSPDEV\n"
            "CacheDir = cache/dir\n"
            "DBPath=db/path\n"
            "\n"
            "[minigalaxy]\n"
            "Server = https://github.com/sharkwouter/arch-repo-test/releases/latest/download\n"
        )
        with patch("builtins.open", mock_open(read_data=data)):
            config = Config()

        self.assertEqual("/base/dir", config.base_directory)
        self.assertEqual("/home/test/pspdev/cache/dir", config.options.cache_dir)
        self.assertEqual("/home/test/pspdev/db/path", config.options.db_path)
        self.assertEqual("/home/test/pspdev", config.options.root_dir)
        self.assertEqual(1, len(config.repositories))

        self.assertEqual("minigalaxy", config.repositories[0].name)
        self.assertEqual(
            "https://github.com/sharkwouter/arch-repo-test/releases/latest/download/minigalaxy.db",
            config.repositories[0].url,
        )

    @patch("os.path.isfile")
    @patch("__main__.__file__", new="/base/dir/boxman")
    def test_init_env_var_root_does_not_exist(self, mock_isfile: MagicMock):
        mock_isfile.return_value = True
        data = (
            "[options]\n"
            "RootDir = $NOTTHERE\n"
            "CacheDir = cache/dir\n"
            "DBPath=db/path\n"
            "\n"
            "[minigalaxy]\n"
            "Server = https://github.com/sharkwouter/arch-repo-test/releases/latest/download\n"
        )
        with patch("builtins.open", mock_open(read_data=data)):
            self.assertRaisesRegex(
                Exception,
                r"Could not expand .* because an environment variable is not set",
                Config,
            )

    @patch("os.path.isfile")
    @patch("__main__.__file__", new="/base/dir/boxman")
    def test_init_defaults(self, mock_isfile: MagicMock):
        mock_isfile.return_value = True
        with patch("builtins.open", mock_open(read_data="")):
            config = Config()

        self.assertEqual("/base/dir", config.base_directory)
        self.assertEqual("/base/dir/var/cache/boxman", config.options.cache_dir)
        self.assertEqual("/base/dir/var/lib/boxman", config.options.db_path)
        self.assertEqual("/base/dir", config.options.root_dir)
        self.assertEqual(0, len(config.repositories))

    @patch("os.path.isfile")
    @patch("__main__.__file__", new="/base/dir/boxman")
    def test_get_relative_path(self, mock_isfile: MagicMock):
        mock_isfile.return_value = True
        with patch("builtins.open", mock_open(read_data="")):
            config = Config()

        self.assertEqual("/base/dir/", config.get_relative_path("/"))
        self.assertEqual("/base/dir/root/.ssh", config.get_relative_path("/root/.ssh"))
        self.assertEqual("/base/dir/", config.get_relative_path("/../../.."))
        self.assertEqual("/base/dir/root", config.get_relative_path("//////root"))
        self.assertEqual("/base/dir/root", config.get_relative_path("/../../../root"))
        self.assertEqual("/base/dir/root", config.get_relative_path("root"))

    @patch("sys.platform", new="win32")
    @patch("os.path.dirname")
    @patch("os.path.join")
    @patch("os.path.isfile")
    def test_get_relative_path_windows(
        self, mock_isfile: MagicMock, mock_join: MagicMock, mock_dirname
    ):
        mock_isfile.return_value = True
        mock_dirname.return_value = "C:\\root"
        with patch("builtins.open", mock_open(read_data="")):
            config = Config()

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

    @patch("sys.exit")
    @patch("os.path.isfile")
    def test_init_config_does_not_exist(
        self, mock_isfile: MagicMock, mock_exit: MagicMock
    ):
        mock_isfile.return_value = False
        mock_exit.side_effect = Exception("test_init_config_does_not_exist")
        self.assertRaisesRegex(Exception, "test_init_config_does_not_exist", Config)
        mock_exit.assert_called_once_with("No configuration file was found")
