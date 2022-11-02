from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock

from boxman import LocalDatabase


class TestLocalDatabase(TestCase):
    @patch("os.makedirs")
    @patch("os.path.isdir")
    def test_init(self, mock_isdir: MagicMock, mock_makedirs: MagicMock):
        mock_isdir.return_value = True
        config = MagicMock()
        config.options.db_path = "/home/user/pspdev/var/lib/pacman"
        db = LocalDatabase(config)
        self.assertEqual(
            "/home/user/pspdev/var/lib/pacman/local", db._LocalDatabase__local_directory
        )
        mock_makedirs.assert_not_called()

    @patch("os.makedirs")
    @patch("os.path.isdir")
    def test_init_directory_creation(
        self, mock_isdir: MagicMock, mock_makedirs: MagicMock
    ):
        mock_isdir.return_value = False
        with patch("builtins.open", mock_open()):
            config = MagicMock()
            config.options.db_path = "/home/user/pspdev/var/lib/pacman"
            LocalDatabase(config)
        mock_makedirs.assert_called_once_with("/home/user/pspdev/var/lib/pacman/local")

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_package_directory(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock
    ):
        mock_isdir.return_value = True
        config = MagicMock()
        config.options.db_path = "/test/var/lib/pacman"
        db = LocalDatabase(config)

        mock_listdir.return_value = ["test-1.0.1-1"]

        self.assertEqual("test-1.0.1-1", db.get_package_directory("test"))

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_desc(self, mock_isdir: MagicMock, mock_listdir: MagicMock):
        mock_isdir.return_value = True
        mock_listdir.return_value = [
            "libpspvram-r11.885fd3f-1",
            "pspgl-r12-1",
            "pspirkeyb-r1-1",
            "sdl-1.2.15-1",
            "sdl2-2.25.0-3",
        ]
        desc_content = """%NAME%
sdl2


%VERSION%
2.25.0-3


%BASE%
sdl2


%ARCH%
mips


%BUILDDATE%
1666723000


%INSTALLDATE%
1667168130


%SIZE%
4052133


%VALIDATION%
md5
sha256


"""
        config = MagicMock()
        config.options.db_path = "/test/var/lib/pacman"
        db = LocalDatabase(config)
        mock_open_desc_file = MagicMock()
        with patch(
            "builtins.open", mock_open(mock_open_desc_file, read_data=desc_content)
        ):
            desc = db.get_package_desc("sdl2")
            self.assertEqual(desc_content, repr(desc))
            mock_open_desc_file.assert_called_once_with(
                "/test/var/lib/pacman/local/sdl2-2.25.0-3/desc", "r"
            )

    @patch("os.path.isdir")
    def test_install_desc(self, mock_isdir: MagicMock):
        mock_isdir.return_value = True
        config = MagicMock()
        config.options.db_path = "/test/var/lib/pacman"
        db = LocalDatabase(config)

        desc = MagicMock()
        files = MagicMock()
        mock_writer = MagicMock()
        with patch("builtins.open", mock_open(mock_writer)):
            db.install(desc, files)
            self.assertEqual(mock_writer.call_count, 2)

    @patch("os.makedirs")
    @patch("os.path.isdir")
    def test_install_desc_can_make_directory(
        self, mock_isdir: MagicMock, mock_makedirs: MagicMock
    ):
        mock_isdir.side_effect = [True, False]
        config = MagicMock()
        config.options.db_path = "/test/var/lib/pacman"
        db = LocalDatabase(config)
        mock_makedirs.assert_not_called()

        desc = MagicMock()
        files = MagicMock()
        mock_writer = MagicMock()
        with patch("builtins.open", mock_open(mock_writer)):
            db.install(desc, files)
            mock_makedirs.assert_called_once()
            self.assertEqual(mock_writer.call_count, 2)

    @patch("os.listdir")
    @patch("os.path.isdir")
    def test_get_package_directories(
        self, mock_isdir: MagicMock, mock_listdir: MagicMock
    ):
        mock_isdir.return_value = True
        config = MagicMock()
        config.options.db_path = "/home/user/pspdev/var/lib/pacman"
        db = LocalDatabase(config)

        mock_listdir.return_value = [
            "libpspvram-r11.885fd3f-1",
            "pspgl-r12-1",
            "pspirkeyb-r1-1",
            "sdl-1.2.15-1",
            "sdl2-2.25.0-3",
            "does-not-match",
            "somefile",
            "this-is-a-test",
        ]

        expected = [
            "libpspvram-r11.885fd3f-1",
            "pspgl-r12-1",
            "pspirkeyb-r1-1",
            "sdl-1.2.15-1",
            "sdl2-2.25.0-3",
        ]

        actual = db.get_package_directories()

        self.assertEqual(expected, actual)
