import os

from boxman import Config
from boxman.data.config.repository import Repository


class DatabaseManager:
    def __init__(self, repository: Repository, config: Config, refresh_after: int = 30):
        """

        :param refresh_after: Refresh the database after the specified amount of minutes
        """
        self.database_url = repository.database_url
        self.database_file = os.path.join(
            config.options.db_path, f"{repository.name}.db"
        )

        self.refresh_after = refresh_after

    def refresh(self):
        pass

    def get_packages(self):
        pass
