import os
from hashlib import sha256, md5
from typing import Optional


def checksums_match(
    file_path: str, md5_checksum: Optional[str], sha256_checksum: Optional[str]
) -> bool:
    if not os.path.isfile(file_path):
        return False

    match = True
    with open(file_path, "rb") as file:
        content = file.read()
        if md5_checksum:
            if not md5(content).hexdigest() == md5_checksum:
                match = False
        if sha256_checksum:
            if not sha256(content).hexdigest() == sha256_checksum:
                match = False
    return match
