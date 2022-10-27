from unittest import TestCase

from boxman.repository import Repository


class TestRepository(TestCase):
    def test_init(self):
        repo = Repository("name", "https://example.com/repo", "/root")
        self.assertEqual("name", repo.name)
        self.assertEqual("https://example.com/repo/name.db", repo.url)
        self.assertEqual("/root/name.db", repo.path)
        self.assertEqual("/root", repo.dir)
