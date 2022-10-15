from unittest import TestCase

from boxman.data.config.repository import Repository


class TestRepository(TestCase):
    def test_init(self):
        repo = Repository("name", "https://example.com/repo")
        self.assertEqual("name", repo.name)
        self.assertEqual("https://example.com/repo", repo.server)
        self.assertEqual("https://example.com/repo/name.db", repo.database_url)
