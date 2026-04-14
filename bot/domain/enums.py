from enum import Enum

class EssenceType(str, Enum):
    EARTH = "Earth"
    WIND = "Wind"
    FIRE = "Fire"
    ARCANE = "Arcane"
    WATER = "Water"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

class SpiritType(str, Enum):
    FELINE = "Feline"
    CANINE = "Canine"
    WINGED = "Winged"
    GOBLIN = "Goblin"
    RESTLESS = "Restless"

class Rarity(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"

class EncounterType(str, Enum):
    ESSENCE = "essence"
    SPIRIT = "spirit"

class ResonanceMode(str, Enum):
    ECHO = "echo"
    PULSE = "pulse"
    ATTRACT = "attract"

class LureType(str, Enum):
    ESSENCE = "essence"
    SPIRIT = "spirit"
    PURE = "pure"
