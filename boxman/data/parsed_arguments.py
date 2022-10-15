from dataclasses import dataclass
from typing import List, Optional

from boxman.data.mode import Mode


@dataclass
class ParsedArguments:
    mode: Mode
    arguments: Optional[List[str]] = None
