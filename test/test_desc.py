from unittest import TestCase

from boxman.desc import Desc


class TestDesc(TestCase):
    def test_init(self):
        data = """%FILENAME%
pspirkeyb-r1-1-mips.pkg.tar.gz

%NAME%
pspirkeyb

%BASE%
pspirkeyb

%VERSION%
r1-1

%DESC%
a library for using IRDA keyboards with Playstation Portable

%CSIZE%
49378

%ISIZE%
135283

%MD5SUM%
52976c1ef3ebad0f981b1e240c111034

%SHA256SUM%
bd5d0538e945a456dc3b5001377b3ff5079065ce6f4ab686fbbb14e1d1ec9c12

%URL%
https://github.com/pspdev/psp-ports

%LICENSE%
LGPL2.1

%ARCH%
mips

%BUILDDATE%
1666255374

%PACKAGER%
Unknown Packager

"""
        desc = Desc(data, "pspdev")

        # Test if the values can be retrieved in the expected manner
        self.assertEqual("pspirkeyb-r1-1-mips.pkg.tar.gz", desc.file_name)
        self.assertEqual("pspirkeyb", desc.name)
        self.assertEqual("pspirkeyb", desc.base)
        self.assertEqual("r1-1", str(desc.version))
        self.assertEqual("a library for using IRDA keyboards with Playstation Portable", desc.description)
        self.assertEqual(49378, desc.compressed_size)
        self.assertEqual(135283, desc.size)
        self.assertEqual("52976c1ef3ebad0f981b1e240c111034", desc.md5_checksum)
        self.assertEqual("bd5d0538e945a456dc3b5001377b3ff5079065ce6f4ab686fbbb14e1d1ec9c12", desc.sha256_checksum)
        self.assertEqual("https://github.com/pspdev/psp-ports", desc.url)
        self.assertEqual(["LGPL2.1"], desc.licenses)
        self.assertEqual("mips", desc.architecture)
        self.assertEqual(1666255374, desc.build_date)
        self.assertEqual("Unknown Packager", desc.packager)

    def test_repr(self):
        data = """%FILENAME%
pspirkeyb-r1-1-mips.pkg.tar.gz

%NAME%
pspirkeyb

%BASE%
pspirkeyb

%VERSION%
r1-1

%DESC%
a library for using IRDA keyboards with Playstation Portable

%CSIZE%
49378

%ISIZE%
135283

%MD5SUM%
52976c1ef3ebad0f981b1e240c111034

%SHA256SUM%
bd5d0538e945a456dc3b5001377b3ff5079065ce6f4ab686fbbb14e1d1ec9c12

%URL%
https://github.com/pspdev/psp-ports

%LICENSE%
LGPL2.1

%ARCH%
mips

%BUILDDATE%
1666255374

%PACKAGER%
Unknown Packager

"""
        desc = Desc(data, "pspdev")
        self.assertSetEqual(set(data.split("\n")), set(repr(desc).split("\n")))

    def test_to_string(self):
        data = """%FILENAME%
pspirkeyb-r1-1-mips.pkg.tar.gz

%NAME%
pspirkeyb

%BASE%
pspirkeyb

%VERSION%
r1-1

%DESC%
a library for using IRDA keyboards with Playstation Portable

%CSIZE%
49378

%ISIZE%
135283

%MD5SUM%
52976c1ef3ebad0f981b1e240c111034

%SHA256SUM%
bd5d0538e945a456dc3b5001377b3ff5079065ce6f4ab686fbbb14e1d1ec9c12

%URL%
https://github.com/pspdev/psp-ports

%LICENSE%
LGPL2.1

%ARCH%
mips

%BUILDDATE%
1666255374

%PACKAGER%
Unknown Packager

"""
        desc = Desc(data, "pspdev")
        expected = """Repository      : pspdev
Name            : pspirkeyb
Version         : r1-1
Description     : a library for using IRDA keyboards with Playstation Portable
Architecture    : mips
URL             : https://github.com/pspdev/psp-ports
Licenses        : LGPL2.1
Groups          : None
Provides        : None
Depends On      : None
Optional Deps   : None
Conflicts With  : None
Replaces        : None
Download Size   : 48.22 KiB
Installed Size  : 132.11 KiB
Packager        : Unknown Packager
Build Date      : Thu Oct 20 10:42:54 2022
Validated By    : MD5 Sum  SHA-256 Sum

"""
        self.assertEqual(expected, str(desc))
