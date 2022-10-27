import logging
import re
import time
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PackageDescription:
    name: str
    base: str
    version: str
    description: str
    url: str
    arch: str
    packager: str
    license: List[str]
    build_date: int
    dependencies: List[str]
    optional_dependencies: Optional[List[str]] = None
    build_dependencies: Optional[List[str]] = None
    provides: Optional[List[str]] = None
    size: Optional[int] = None
    install_size: Optional[int] = None
    compressed_size: Optional[int] = None
    md5_checksum: Optional[str] = None
    sha256_checksum: Optional[str] = None
    install_date: Optional[int] = None
    reason: Optional[int] = None
    file_name: Optional[str] = None
    pgp_signature: Optional[str] = None
    validation: Optional[str] = None

    def __str__(self):  # noqa: C901
        result = ""
        if self.file_name:
            result += f"%FILENAME%\n{self.file_name}\n\n"
        result += f"%NAME%\n{self.name}\n\n"
        result += f"%BASE%\n{self.base}\n\n"
        result += f"%VERSION%\n{self.version}\n\n"
        result += f"%DESC%\n{self.description}\n\n"
        if self.compressed_size:
            result += f"%CSIZE%\n{self.compressed_size}\n\n"
        if self.install_size:
            result += f"%ISIZE%\n{self.install_size}\n\n"
        if self.md5_checksum:
            result += f"%MD5SUM%\n{self.md5_checksum}\n\n"
        if self.sha256_checksum:
            result += f"%SHA256SUM%\n{self.sha256_checksum}\n\n"
        if self.pgp_signature:
            result += f"%PGPSIG%\n{self.sha256_checksum}\n\n"
        result += f"%URL%\n{self.url}\n\n"

        license_string = "\n".join(self.license)
        result += f"%LICENSE%\n{license_string}\n\n"
        result += f"%ARCH%\n{self.arch}\n\n"
        if self.size:
            result += f"%SIZE%\n{self.size}\n\n"
        if self.validation:
            result += f"%VALIDATE%\n{self.validation}\n\n"
        if self.reason:
            result += f"%REASON%\n{self.reason}\n\n"
        dependencies_string = "\n".join(self.dependencies)
        result += f"%DEPENDS%\n{dependencies_string}\n\n"
        if self.optional_dependencies:
            optional_dependencies_string = "\n".join(self.optional_dependencies)
            result += f"%OPTDEPENDS%\n{optional_dependencies_string}\n\n"
        if self.build_dependencies:
            build_dependencies_string = "\n".join(self.build_dependencies)
            result += f"%MAKEDEPENDS%\n{build_dependencies_string}\n\n"
        if self.provides:
            provides_string = "\n".join(self.provides)
            result += f"%PROVIDES%\n{provides_string}\n\n"

        return result

    def convert_to_local(self, reason: Optional[int] = None) -> None:
        """
        Convert to a local
        :param reason: Set to 1 if this is a dependency
        :return:
        """
        self.reason = reason
        if not self.install_date:
            self.install_date = int(time.time())
        if self.install_size:
            self.size = self.install_size
            self.install_size = None

        self.compressed_size = None
        self.md5_checksum = None
        self.sha256_checksum = None
        self.build_dependencies = None


def parse_desc(content: str) -> PackageDescription:  # noqa: C901
    package_description = PackageDescription(
        name="",
        base="",
        version="",
        description="",
        url="",
        arch="",
        packager="",
        license=[],
        build_date=0,
        dependencies=[],
    )
    current_header: Optional[str] = None
    for line in content.split("\n"):
        if not line:
            continue
        if re.match(r"^%[A-Z\d]+%$", line):
            current_header = line
            logging.debug(f"found header {line}")
            continue

        if current_header == "%FILENAME%":
            package_description.file_name = line
        elif current_header == "%NAME%":
            package_description.name = line
        elif current_header == "%BASE%":
            package_description.base = line
        elif current_header == "%VERSION%":
            package_description.version = line
        elif current_header == "%DESC%":
            package_description.description = line
        elif current_header == "%CSIZE%":
            package_description.compressed_size = int(line)
        elif current_header == "%ISIZE%":
            package_description.install_size = int(line)
        elif current_header == "%MD5SUM%":
            package_description.md5_checksum = line
        elif current_header == "%SHA256SUM%":
            package_description.sha256_checksum = line
        elif current_header == "%URL%":
            package_description.url = line
        elif current_header == "%LICENSE%":
            package_description.license.append(line)
        elif current_header == "%ARCH%":
            package_description.arch = line
        elif current_header == "%BUILDDATE%":
            package_description.build_date = int(line)
        elif current_header == "%PACKAGER%":
            package_description.packager = line
        elif current_header == "%DEPENDS%":
            package_description.dependencies.append(line)
        elif current_header == "%OPTDEPENDS%":
            if package_description.optional_dependencies is None:
                package_description.optional_dependencies = []
            package_description.optional_dependencies.append(line)
        elif current_header == "%MAKEDEPENDS%":
            if package_description.build_dependencies is None:
                package_description.build_dependencies = []
            package_description.build_dependencies.append(line)
        else:
            print(f"No else statement for header {current_header}")

    return package_description
