import logging
import re
import time
from dataclasses import dataclass
from typing import Optional, List, Dict


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
    validation: Optional[List[str]] = None

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


class Desc:
    __values: Dict
    __source: str

    def __init__(self, content, source):
        self.__fill_values(content)
        self.__validate_values()

        self.__source = source

    def __fill_values(self, content: str):
        self.__values = {}
        key = None

        for line in content.split("\n"):
            if not line:
                continue

            if re.match(r"^%[A-Z\d]+%$", line):
                key = line.strip("%")
                self.__values[key] = []
                continue

            if not key:
                continue

            self.__values[key].append(line)

    def __validate_values(self):
        required_keys = ["NAME", "VERSION", "ARCH"]
        for key in required_keys:
            assert key in self.__values
            assert len(self.__values[key]) > 0

    def __repr__(self):
        result = ""
        for key in self.__values:
            result += f"%{key}%\n"
            for value in self.__values[key]:
                result += f"{value}\n"
            result += "\n\n"
        return result

    def __str__(self):
        description = self.description.replace("\n", "\n                  ")
        licenses = " ".join(self.licenses) if len(self.licenses) > 0 else None
        groups = " ".join(self.groups) if len(self.groups) > 0 else None
        provides = " ".join(self.provides) if len(self.provides) > 0 else None
        dependencies = (
            " ".join(self.dependencies) if len(self.dependencies) > 0 else None
        )
        optional_dependencies = (
            " ".join(self.optional_dependencies)
            if len(self.optional_dependencies) > 0
            else None
        )
        conflicts_with = (
            " ".join(self.conflicts_with) if len(self.conflicts_with) > 0 else None
        )
        replaces = " ".join(self.replaces) if len(self.replaces) > 0 else None
        download_size = (
            f"{self.compressed_size / 1024 :.2f} KiB" if self.compressed_size else None
        )
        installed_size = f"{self.size / 1024:.2f} KiB"
        build_date = time.ctime(self.build_date)
        validated_by = (
            " ".join(self.validated_by) if len(self.validated_by) > 0 else None
        )
        return (
            f"Repository      : {self.source}\n"
            f"Name            : {self.name}\n"
            f"Version         : {self.version}\n"
            f"Description     : {description}\n"
            f"Architecture    : {self.architecture}\n"
            f"URL             : {self.url}\n"
            f"Licenses        : {licenses}\n"
            f"Groups          : {groups}\n"
            f"Provides        : {provides}\n"
            f"Depends On      : {dependencies}\n"
            f"Optional Deps   : {optional_dependencies}\n"
            f"Conflicts With  : {conflicts_with}\n"
            f"Replaces        : {replaces}\n"
            f"Download Size   : {download_size}\n"
            f"Installed Size  : {installed_size}\n"
            f"Packager        : {self.packager}\n"
            f"Build Date      : {build_date}\n"
            f"Validated By    : {validated_by}\n"
            "\n"
        )

    @property
    def source(self) -> str:
        return self.__source

    @property
    def name(self) -> str:
        """
        Name of the package without version information
        """
        return self.__values["NAME"][0]

    @property
    def version(self) -> str:
        """
        Package version in format "version-build", example: 1.0.1-4
        """
        return self.__values["VERSION"][0]

    @property
    def architecture(self) -> str:
        """
        The CPU architecture the package was build for
        """
        return self.__values["ARCH"][0]

    @property
    def description(self) -> str:
        """
        Description of the package
        """
        if "DESC" in self.__values and len(self.__values["DESC"]) > 0:
            return "/n".join(self.__values["DESC"])
        return ""

    @property
    def groups(self) -> List[str]:
        """
        Package groups to which the package was assigned
        """
        if "GROUPS" in self.__values and len(self.__values["GROUPS"]) > 0:
            return self.__values["GROUPS"]
        return []

    @property
    def url(self) -> str:
        """
        URL to the homepage of the package
        """
        if "URL" in self.__values and len(self.__values["URL"]) > 0:
            return self.__values["URL"][0]
        return ""

    @property
    def packager(self) -> str:
        """
        Name and possibly email of packager in "Firstname Lastname <email>" format
        """
        if "PACKAGER" in self.__values and len(self.__values["PACKAGER"]) > 0:
            return self.__values["PACKAGER"][0]
        return "Unknown Packager"

    @property
    def provides(self) -> List[str]:
        """
        Binaries provided which could potentially conflict with other packages.
        Set manually by the packager.
        """
        if "PROVIDES" in self.__values and len(self.__values["PROVIDES"]) > 0:
            return self.__values["PROVIDES"]
        return []

    @property
    def dependencies(self) -> List[str]:
        """
        Packages which need to be installed for this package to be usable
        """
        if "DEPENDS" in self.__values and len(self.__values["DEPENDS"]) > 0:
            return self.__values["DEPENDS"]
        return []

    @property
    def optional_dependencies(self) -> List[str]:
        """
        Packages which can be installed to enhance the functionality of this package
        """
        if "OPTDEPENDS" in self.__values and len(self.__values["OPTDEPENDS"]) > 0:
            return self.__values["OPTDEPENDS"]
        return []

    @property
    def build_dependencies(self) -> List[str]:
        """
        Packages which need to be installed to be able to build this package
        """
        if "MAKEDEPENDS" in self.__values and len(self.__values["MAKEDEPENDS"]) > 0:
            return self.__values["MAKEDEPENDS"]
        return []

    @property
    def licenses(self) -> List[str]:
        if "LICENSE" in self.__values and len(self.__values["LICENSE"]) > 0:
            return self.__values["LICENSE"]
        return []

    @property
    def conflicts_with(self) -> List[str]:
        """
        Packages which cannot be installed on the same system as this package
        """
        if "CONFLICTS" in self.__values and len(self.__values["CONFLICTS"]) > 0:
            return self.__values["CONFLICTS"]
        return []

    @property
    def replaces(self) -> List[str]:
        """
        For which packages this package should be installed as a replacement
        """
        if "REPLACES" in self.__values and len(self.__values["REPLACES"]) > 0:
            return self.__values["REPLACES"]
        return []

    @property
    def validated_by(self) -> List[str]:
        """
        Which types of validators can be used to validate this package
        """
        result = []
        if "VALIDATE" in self.__values and len(self.__values["VALIDATE"]) > 0:
            result += self.__values["VALIDATE"]
        if "MD5SUM" in self.__values and "MD5 Sum" not in result:
            result.append("MD5 Sum")
        if "SHA256SUM" in self.__values and "SHA-256 Sum" not in result:
            result.append("SHA-256 Sum")
        if "PGPSIG" in self.__values and "Signature" not in result:
            result.append("Signature")

        return result

    @property
    def installed_as_dependency(self) -> bool:
        """
        Whether this package was installed automatically as a dependency or not
        """
        if "REASON" in self.__values and len(self.__values["REASON"]) > 0:
            return self.__values["REASON"][0] == 1
        return False

    @property
    def size(self) -> int:
        """
        Return size of package when installed
        """
        if "ISIZE" in self.__values and len(self.__values["ISIZE"]) > 0:
            return int(self.__values["ISIZE"][0])
        if "SIZE" in self.__values and len(self.__values["SIZE"]) > 0:
            return int(self.__values["SIZE"][0])

    @property
    def compressed_size(self) -> Optional[int]:
        """
        Return size of package when installed
        """
        if "CSIZE" in self.__values and len(self.__values["CSIZE"]) > 0:
            return int(self.__values["CSIZE"][0])

    @property
    def build_date(self) -> int:
        if "BUILDDATE" in self.__values and len(self.__values["BUILDDATE"]) > 0:
            return int(self.__values["BUILDDATE"][0])
        return 0


# def parse_desc2(content: str):
#     d = parse_desc_to_dict(content)
#
#     return PackageDescription(
#         name=d["NAME"][0],
#         base=["BASE"][0],
#         version=d["VERSION"][0],
#         description="\n".join(d["DESC"]),
#         url=d["URL"][0],
#         arch=d["ARCH"][0],
#         packager=d["PACKAGER"][0],
#         license=d["LICENSE"],
#         build_date=int(d["BUILDDATE"][0]),
#         dependencies=d["DEPENDS"],
#
#         # Now optional fields
#         optional_dependencies=d["OPTDEPENDS"] if "OPTDEPENDS" in d else None,
#         build_dependencies=d["MAKEDEPENDS"] if "MAKEDEPENDS" in d else None,
#         provides=d["PROVIDES"] if "PROVIDES" in d else None,
#         size=int(d["SIZE"][0]) if "SIZE" in d else None,
#         install_size=int(d["ISIZE"][0]) if "ISIZE" in d else None,
#         compressed_size=int(d["CSIZE"][0]) if "CSIZE" in d else None,
#         md5_checksum=d["MD5SUM"][0] if "MD5SUM" in d else None,
#         sha256_checksum=d["SHA256SUM"][0] if "SHA256SUM" in d else None,
#         install_date=int(d["INSTALLDATE"][0]) if "INSTALLDATE" in d else None,
#         reason=d["REASON"][0] if "REASON" in d else None,
#         file_name=d["FILENAME"][0] if "FILENAME" in d else None,
#         pgp_signature=d["PGPSIG"][0] if "PGPSIG" in d else None,
#         validation=d["VALIDATION"] if "VALIDATION" in d else None,
#     )
