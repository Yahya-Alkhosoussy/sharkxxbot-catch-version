from dataclasses import dataclass
from enum import StrEnum


class Nets(StrEnum):
    ROPE = "rope net"
    LEATHER = "leather net"
    GOLD = "gold net"
    TITANIUM = "titanium net"
    DOOM = "net of doom"

class Rarity(StrEnum):
    TRASH = "trash"
    COMMON = "common"
    SHINY = "shiny"
    LEGENDARY = "legendary"

@dataclass(frozen=True)
class Fish:
    rarity: Rarity
    net_used: Nets
