import os
import tarfile
from typing import List, Optional


def extract(archive: str, destination: str) -> None:
    if not tarfile.is_tarfile(archive):
        raise Exception(f"{archive} is not a valid tar archive")
    with tarfile.open(archive) as t:
        for member in t.getmembers():
            print(member.path)
        # t.extractall(destination)


def get_files_in_archive(archive: str) -> List[str]:
    if not tarfile.is_tarfile(archive):
        raise Exception(f"{archive} is not a valid tar archive")
    files = []
    with tarfile.open(archive) as t:
        for member in t.getmembers():
            files.append(member.name)
    return files


def get_packages_in_database_archive(archive: str) -> List[str]:
    if not tarfile.is_tarfile(archive):
        raise Exception(f"{archive} is not a valid tar archive")
    files = []
    with tarfile.open(archive) as t:
        for member in t.getmembers():
            if member.isdir():
                package_name, package_version, package_rel = os.path.basename(
                    member.name
                ).rsplit("-", 2)
                files.append(f"{package_name} {package_version}-{package_rel}")
    return files


def read_file_in_archive(archive: str, file_name: str) -> Optional[str]:
    if not tarfile.is_tarfile(archive):
        raise Exception(f"{archive} is not a valid tar archive")
    with tarfile.open(archive) as t:
        for member in t.getmembers():
            print(member.name)
            if file_name == member.name:
                output = t.extractfile(member).read().decode()
                t.close()
                return output
    return None


def extract_file(archive: str, file_name: str, destination: str) -> None:
    if not tarfile.is_tarfile(archive):
        raise Exception(f"{archive} is not a valid tar archive")
    with tarfile.open(archive) as t:
        for member in t.getmembers():
            if file_name == member.name:
                with open(destination, "wb") as file_dest:
                    file_dest.write(t.extractfile(member).read())
                t.close()
