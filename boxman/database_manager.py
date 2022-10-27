import os
import shutil
import time
from tempfile import TemporaryDirectory
from typing import Callable

from boxman import Config
from boxman.archive import get_packages_in_database_archive
from boxman.download import download


def download_database(func: Callable):
    def inner(self, *args, **kwargs):
        for repository in self.config.repositories:
            database_file = repository.get_database_path(self.config.options.db_path)
            if not os.path.isfile(database_file):
                download_directory = os.path.dirname(database_file)
                if not os.path.isdir(download_directory):
                    os.makedirs(download_directory)
                print(f"Downloading database {repository.name}")
                self._download_database()
            else:
                mtime = os.path.getmtime(database_file)
                minutes_since_last_edit = int((time.time() - mtime) / 60)
                if minutes_since_last_edit >= self.refresh_after:
                    print(
                        f"Redownloading database {repository.name}, time expired was {minutes_since_last_edit}"
                    )
                    self._download_database()
        return func(self, *args, **kwargs)

    return inner


class DatabaseManager:
    def __init__(self, config: Config, refresh_after: int = 30):
        """

        :param refresh_after: Refresh the database after the specified amount of minutes
        """
        self.config = config
        self.refresh_after = refresh_after

    def _download_database(self):
        with TemporaryDirectory() as temp_dir:
            for repository in self.config.repositories:
                database_file = repository.get_database_path(
                    self.config.options.db_path
                )
                temp_location = os.path.join(temp_dir, os.path.basename(database_file))
                download(repository.database_url, temp_location)
                try:
                    os.rename(temp_location, database_file)
                except OSError:
                    shutil.copy(temp_location, database_file)

    @download_database
    def get_packages(self):
        packages = []
        for repository in self.config.repositories:
            database_file = repository.get_database_path(self.config.options.db_path)
            packages += get_packages_in_database_archive(database_file)

        return packages
