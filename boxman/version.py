import re
from typing import List


class Version:
    version: str
    version_parts: List[int]

    def __init__(self, version_string: str):
        self.version = version_string

        self.__generate_version_parts()

    def __generate_version_parts(self):
        sanitized_version_string = ""
        for letter in self.version.replace("-", "."):
            if letter.isdecimal() or letter == ".":
                sanitized_version_string += letter
        if len(sanitized_version_string) == 0 or not re.match(
            r"(\d+\.?)+", sanitized_version_string
        ):
            raise Exception("Cannot parse string")

        self.version_parts = []
        for part in sanitized_version_string.split("."):
            if len(part) > 0:
                self.version_parts.append(int(part))

    def __lt__(self, other) -> bool:
        iterations = max(len(self.version_parts), len(other.version_parts))
        for i in range(iterations):
            if i == len(self.version_parts):
                return True
            elif i == len(other.version_parts):
                return False
            elif self.version_parts[i] == other.version_parts[i]:
                continue
            elif self.version_parts[i] < other.version_parts[i]:
                return True
            else:
                return False
        return False

    def __gt__(self, other):
        iterations = max(len(self.version_parts), len(other.version_parts))
        for i in range(iterations):
            if i == len(self.version_parts):
                return False
            elif i == len(other.version_parts):
                return True
            elif self.version_parts[i] == other.version_parts[i]:
                continue
            elif self.version_parts[i] > other.version_parts[i]:
                return True
            else:
                return False
        return False

    def __str__(self):
        return self.version

    def __repr__(self):
        version_part_strings = []
        for part in self.version_parts:
            version_part_strings.append(str(part))
        return ".".join(version_part_strings)
