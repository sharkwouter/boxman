from unittest import TestCase
from unittest.mock import patch, MagicMock

from boxman.download import download, print_download_progress


class TestDownload(TestCase):
    @patch("os.path.isdir")
    @patch("urllib.request.urlretrieve")
    def test_download(
        self,
        mock_urlretrieve: MagicMock,
        mock_isdir: MagicMock,
    ):
        mock_isdir.return_value = True
        download("http://example.com/", "/some/directory/test.tar.gz")

        mock_urlretrieve.assert_called_once_with(
            "http://example.com/", "/some/directory/test.tar.gz", reporthook=None
        )

    @patch("os.makedirs")
    @patch("os.path.isdir")
    @patch("urllib.request.urlretrieve")
    def test_download_makes_directory(
        self,
        mock_urlretrieve: MagicMock,
        mock_isdir: MagicMock,
        mock_makedirs: MagicMock,
    ):
        mock_isdir.return_value = False
        download("http://example.com/", "/some/directory/test.tar.gz")

        mock_makedirs.assert_called_once_with("/some/directory")
        mock_urlretrieve.assert_called_once_with(
            "http://example.com/", "/some/directory/test.tar.gz", reporthook=None
        )

    @patch("os.path.isdir")
    @patch("urllib.request.urlretrieve")
    def test_download_set_report_progress(
        self,
        mock_urlretrieve: MagicMock,
        mock_isdir: MagicMock,
    ):
        mock_isdir.return_value = True
        download("http://example.com/", "/some/directory/test.tar.gz", True)

        mock_urlretrieve.assert_called_once_with(
            "http://example.com/",
            "/some/directory/test.tar.gz",
            reporthook=print_download_progress,
        )

    @patch("builtins.print")
    def test_print_download_progress(self, mock_print: MagicMock):
        print_download_progress(0, 1000, 10)
        self.assertRegex(
            mock_print.call_args_list[mock_print.call_count - 1].args[0], r"(.* |^)0%.*"
        )

        print_download_progress(0, 10, 100)
        self.assertRegex(
            mock_print.call_args_list[mock_print.call_count - 1].args[0], r"(.* |^)0%.*"
        )

        print_download_progress(1, 10, 100)
        self.assertRegex(
            mock_print.call_args_list[mock_print.call_count - 1].args[0],
            r"(.* |^)10%.*",
        )

        print_download_progress(5, 10, 100)
        self.assertRegex(
            mock_print.call_args_list[mock_print.call_count - 1].args[0],
            r"(.* |^)50%.*",
        )

        print_download_progress(1, 1000, 10)
        self.assertRegex(
            mock_print.call_args_list[mock_print.call_count - 1].args[0],
            r"(.* |^)100%.*",
        )
