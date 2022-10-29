from unittest import TestCase

from boxman.version import Version


class TestVersion(TestCase):
    def test_init(self):
        version_and_expected_version_parts = [
            ("12.2.0-1", [12, 2, 0, 1]),
            ("2.66-2", [2, 66, 2]),
            ("20210910_3.1-1", [202109103, 1, 1]),
            ("0.3.113-1", [0, 3, 113, 1]),
            ("1.20.7.r38.ge82d1a6-4", [1, 20, 7, 38, 8216, 4]),
            ("1.0.0.rc16.3-14", [1, 0, 0, 16, 3, 14]),
            ("0.5.11.5-1", [0, 5, 11, 5, 1]),
            ("20220913.f09bebf-1", [20220913, 9, 1]),
            ("6.0.5.arch1-1", [6, 0, 5, 1, 1]),
        ]

        for version, version_parts in version_and_expected_version_parts:
            instance = Version(version)
            self.assertEqual(version, instance.version)
            self.assertEqual(
                version_parts,
                instance.version_parts,
                msg=f"Version parts for {version} do not match up",
            )

    def test_greater_than(self):
        self.assertTrue(Version("1-2") > Version("1-1"))
        self.assertTrue(Version("2-1") > Version("1-4"))
        self.assertTrue(Version("1.0.1-1") > Version("1.0.0-1"))
        self.assertTrue(Version("3.4.arch2-1") > Version("3.4.arch1-1"))
        self.assertTrue(Version("1.0.1-1") > Version("1.0-1"))

        self.assertFalse(Version("1-1") > Version("1-1"))
        self.assertFalse(Version("1-1") > Version("2-1"))
        self.assertFalse(Version("1.0.0-1") > Version("1.0.1-1"))
        self.assertFalse(Version("3.4.arch1-1") > Version("3.4.arch2-1"))
        self.assertFalse(Version("1.0-1") > Version("1.0.1-1"))

    def test_smaller_than(self):
        self.assertTrue(Version("1-1") < Version("2-1"))
        self.assertTrue(Version("1.0.0-1") < Version("1.0.1-1"))
        self.assertTrue(Version("3.4.arch1-1") < Version("3.4.arch2-1"))
        self.assertTrue(Version("1.0-1") < Version("1.0.1-1"))

        self.assertFalse(Version("1-1") < Version("1-1"))
        self.assertFalse(Version("1-2") < Version("1-1"))
        self.assertFalse(Version("2-1") < Version("1-4"))
        self.assertFalse(Version("1.0.1-1") < Version("1.0.0-1"))
        self.assertFalse(Version("3.4.arch2-1") < Version("3.4.arch1-1"))
        self.assertFalse(Version("1.0.1-1") < Version("1.0-1"))
