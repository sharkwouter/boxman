import os
import re
from typing import List, Optional


class Files:
    __files: List[str]
    __root_directory: str

    def __init__(
        self,
        root_directory: str,
        content: Optional[str] = None,
        file_list: Optional[List[str]] = None,
    ):
        """
        Manages files in the root and represents the files file in the local database
        Either content of files has to be set
        :param root_directory: root directory to which files are installed
        :param content: content of the files file
        :param file_list: list of files
        """
        self.__root_directory = root_directory
        if content:
            self.__files = []
            for line in content.split("\n"):
                if not line or line == "%FILES%":
                    continue
                self.__files.append(line)
        elif file_list:
            self.__files = file_list
        else:
            raise Exception("Either content of file_list has to be set")

    def __repr__(self):
        lines = ["%FILES%"] + self.__files + [""]
        return "\n".join(lines)

    def get_files(self):
        result = []
        for file in self.__files:
            full_path = self.get_full_path(file)
            result.append(full_path)
        return result

    def remove_files(self):
        files = self.get_files()
        files.reverse()
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
            elif os.path.isdir(file):
                try:
                    os.rmdir(file)
                except OSError:
                    continue  # If there is still content there, directories can stay
            else:
                print(f"Could not delete not existing file: {file}")

    def get_full_path(self, path: str):
        if ".." in path:
            path = path.replace("..", "")

        while path.startswith("/"):
            path = path[1:]
        while re.match(r"^[A-Za-z]:\\", path):
            path = path[3:]

        return os.path.join(self.__root_directory, path)
