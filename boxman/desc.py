import re
import time
from typing import Optional, List, Dict

from boxman.version import Version


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

    def __eq__(self, other):
        return self.__values == other.__values and self.__source == other.__source

    def __lt__(self, other):
        if self.name != other.name:
            return self.name < other.name

        return self.version < other.version

    def __gt__(self, other):
        if self.name != other.name:
            return self.name > other.name

        return self.version > other.version

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
        licenses = "  ".join(self.licenses) if len(self.licenses) > 0 else None
        groups = "  ".join(self.groups) if len(self.groups) > 0 else None
        provides = "  ".join(self.provides) if len(self.provides) > 0 else None
        dependencies = (
            "  ".join(self.dependencies) if len(self.dependencies) > 0 else None
        )
        optional_dependencies = (
            "  ".join(self.optional_dependencies)
            if len(self.optional_dependencies) > 0
            else None
        )
        conflicts_with = (
            "  ".join(self.conflicts_with) if len(self.conflicts_with) > 0 else None
        )
        replaces = "  ".join(self.replaces) if len(self.replaces) > 0 else None
        download_size = (
            f"{self.compressed_size / 1024 :.2f} KiB" if self.compressed_size else None
        )
        installed_size = f"{self.size / 1024:.2f} KiB"
        build_date = time.ctime(self.build_date)
        validated_by = (
            "  ".join(self.validated_by) if len(self.validated_by) > 0 else None
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

    def convert_to_local(self, installed_explicitly=True):
        self.set_validation()
        new_values = {
            "NAME": self.__values["NAME"],
            "VERSION": self.__values["VERSION"],
            "BASE": self.__values["BASE"],
            "ARCH": self.__values["ARCH"],
            "BUILDDATE": self.__values["BUILDDATE"],
            "INSTALLDATE": [int(time.time())],
            "SIZE": self.__values["ISIZE"],
            "VALIDATION": self.__values["VALIDATION"],
        }

        # Set reason this package is installed
        if not installed_explicitly:
            new_values["REASON"] = 1

        self.__values = new_values

    def __copy_optional_values_to_local_dict(  # noqa: C901
        self, target_dict: Dict
    ) -> None:
        if "DESC" in self.__values:
            target_dict["DESC"] = self.__values["DESC"]
        if "GROUPS" in self.__values:
            target_dict["GROUPS"] = self.__values["GROUPS"]
        if "URL" in self.__values:
            target_dict["URL"] = self.__values["URL"]
        if "LICENSE" in self.__values:
            target_dict["LICENSE"] = self.__values["LICENSE"]
        if "DEPENDS" in self.__values:
            target_dict["DEPENDS"] = self.__values["DEPENDS"]
        if "OPTDEPENDS" in self.__values:
            target_dict["OPTDEPENDS"] = self.__values["OPTDEPENDS"]
        if "MAKEDEPENDS" in self.__values:
            target_dict["MAKEDEPENDS"] = self.__values["MAKEDEPENDS"]
        if "CHECKDEPENDS" in self.__values:
            target_dict["CHECKDEPENDS"] = self.__values["CHECKDEPENDS"]
        if "CONFLICTS" in self.__values:
            target_dict["CONFLICTS"] = self.__values["CONFLICTS"]
        if "PROVIDES" in self.__values:
            target_dict["PROVIDES"] = self.__values["PROVIDES"]
        # XDATA is skipped, because I don't know what it does

    def set_validation(self):
        self.__values["VALIDATION"] = []

        # Pacman would also add pgp if PGPSIG is set, but boxman does no PGP validation
        if "MD5SUM" in self.__values:
            self.__values["VALIDATION"].append("md5")
        if "SHA256SUM" in self.__values:
            self.__values["VALIDATION"].append("sha256")
        if len(self.__values["VALIDATION"]) == 0:
            self.__values["VALIDATION"].append("none")

    @property
    def source(self) -> str:
        """
        Repository in which the package can be found
        """
        return self.__source

    @property
    def name(self) -> str:
        """
        Name of the package without version information
        """
        return self.__values["NAME"][0]

    @property
    def base(self) -> str:
        """
        Name of the package without version information
        """
        return self.__values["BASE"][0]

    @property
    def version(self) -> Version:
        """
        Package version in format "version-build", example: 1.0.1-4
        """
        return Version(self.__values["VERSION"][0])

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

    @property
    def install_date(self) -> Optional[int]:
        if "INSTALLDATE" in self.__values and len(self.__values["INSTALLDATE"]) > 0:
            return int(self.__values["INSTALLDATE"][0])
