from dataclasses import dataclass
from enum import StrEnum


class NetsEnum(StrEnum):
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

class Size(StrEnum):
    LARGE = "large"
    MEDIUM = "medium"
    SMALL = "small"

@dataclass(frozen=True)
class Boost:
    boost: bool
    amount: int

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("Boost amount cannot be less than or equal to 0")


@dataclass()
class Nets:
    net: NetsEnum | str

    def __post_init__(self) -> None:
        if isinstance(self.net, NetsEnum):
            return
        match self.net.lower():
            case NetsEnum.DOOM:
                self.net = NetsEnum.DOOM
            case NetsEnum.TITANIUM:
                self.net = NetsEnum.TITANIUM
            case NetsEnum.GOLD:
                self.net = NetsEnum.GOLD
            case NetsEnum.LEATHER:
                self.net = NetsEnum.LEATHER
            case NetsEnum.ROPE:
                self.net = NetsEnum.ROPE
            case _:
                raise ValueError("That is not a known net")


    @property
    def get_catch_odds(self) -> int:
        match self.net:
            case NetsEnum.DOOM:
                return 100
            case NetsEnum.TITANIUM:
                return 100
            case NetsEnum.GOLD:
                return 85
            case NetsEnum.LEATHER:
                return 75
            case NetsEnum.ROPE:
                return 60
            case _:
                raise ValueError("Net is not in the known nets list")

@dataclass(frozen=True)
class Fish:
    rarity: Rarity
    net_used: Nets
    size: Size
    boost: Boost

    def __get_fish_value_size(self, size: Size, normal_amount: int) -> int:
        match size:
            case Size.LARGE:
                return normal_amount + 4
            case Size.MEDIUM:
                return normal_amount + 2
            case Size.SMALL:
                return normal_amount
            case _:
                raise ValueError("Size isn't one of the known options")


    @property
    def get_coin_value(self) -> int:
        if self.boost:
            match self.rarity:
                case Rarity.TRASH:
                    return 1 * self.boost.amount
                case Rarity.COMMON:
                    return self.__get_fish_value_size(self.size, 2) * self.boost.amount
                case Rarity.SHINY:
                    return self.__get_fish_value_size(self.size, 5) * self.boost.amount
                case Rarity.LEGENDARY:
                    return self.__get_fish_value_size(self.size, 10) * self.boost.amount
                case _:
                    raise ValueError("Rarity is not in the known list of rarities.")
        match self.rarity:
            case Rarity.TRASH:
                return 1
            case Rarity.COMMON:
                return self.__get_fish_value_size(self.size, 2)
            case Rarity.SHINY:
                return self.__get_fish_value_size(self.size, 5)
            case Rarity.LEGENDARY:
                return self.__get_fish_value_size(self.size, 10)
            case _:
                raise ValueError("Rarity is not in the known list of rarities.")
