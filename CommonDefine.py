from enum import IntEnum
from dataclasses import dataclass

# coordinate structure
@dataclass
class TCoor:
    x: int
    y: int

# direction type
class EDirection( IntEnum ):
    none = 0
    up = 1
    down = 2
    left = 3
    right = 4