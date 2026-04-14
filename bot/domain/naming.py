import random
from bot.domain.enums import EssenceType, SpiritType, Rarity

class NamingRules:
    ESSENCE_ADJECTIVES = {
        EssenceType.EARTH: {
            Rarity.COMMON: ["Mossy", "Stoney", "Rooted"],
            Rarity.UNCOMMON: ["Granite", "Verdant", "Thistled"],
            Rarity.RARE: ["Ancient", "Lithic", "Overgrown"],
            Rarity.LEGENDARY: ["World-Born", "Terra-Core", "Tectonic"]
        },
        EssenceType.WIND: {
            Rarity.COMMON: ["Breezy", "Airy", "Drafty"],
            Rarity.UNCOMMON: ["Gale-Force", "Swifty", "Whistling"],
            Rarity.RARE: ["Cyclone", "Sky-Tied", "Zephyr"],
            Rarity.LEGENDARY: ["Aether-Born", "Zenith", "Storm-Chosen"]
        },
        EssenceType.FIRE: {
            Rarity.COMMON: ["Warm", "Flickering", "Glowing"],
            Rarity.UNCOMMON: ["Burning", "Ember", "Singeing"],
            Rarity.RARE: ["Cinder", "Blazing", "Scorch"],
            Rarity.LEGENDARY: ["Solar-Infused", "Inferno", "Core-Fire"]
        },
        EssenceType.ARCANE: {
            Rarity.COMMON: ["Mystic", "Dim", "Strange"],
            Rarity.UNCOMMON: ["Rune-Bound", "Eldritch", "Sparking"],
            Rarity.RARE: ["Celestial", "Astral", "Aetheric"],
            Rarity.LEGENDARY: ["Void-Touched", "Infinite", "Reality-Warper"]
        },
        EssenceType.WATER: {
            Rarity.COMMON: ["Damp", "Fluid", "Mist-Touched"],
            Rarity.UNCOMMON: ["Tidal", "Surge", "Bubbling"],
            Rarity.RARE: ["Wave-Born", "Torrential", "Deep-Sea"],
            Rarity.LEGENDARY: ["Oceanic", "Abyss-Dredged", "Abyssal"]
        }
    }

    SPIRIT_NOUNS = {
        SpiritType.FELINE: {
            Rarity.COMMON: ["Cat", "Kitten", "Stray"],
            Rarity.UNCOMMON: ["Bobcat", "Lynx", "Serval"],
            Rarity.RARE: ["Cougar", "Panther", "Caracal"],
            Rarity.LEGENDARY: ["Great-Cat", "Apex-Stalker", "Void-Leopard"]
        },
        SpiritType.CANINE: {
            Rarity.COMMON: ["Mutt", "Hound", "Pup"],
            Rarity.UNCOMMON: ["Jackal", "Wolf", "Coyote"],
            Rarity.RARE: ["Dire-Wolf", "Husky", "Mastiff"],
            Rarity.LEGENDARY: ["Night-Stalker", "Alpha-Predator", "Storm-Howler"]
        },
        SpiritType.WINGED: {
            Rarity.COMMON: ["Bird", "Sparrow", "Chick"],
            Rarity.UNCOMMON: ["Falcon", "Hawk", "Kestrel"],
            Rarity.RARE: ["Eagle", "Owl", "Vulture"],
            Rarity.LEGENDARY: ["Cloud-Sovereign", "Sky-Reaper", "Sun-Striker"]
        },
        SpiritType.GOBLIN: {
            Rarity.COMMON: ["Imp", "Runt", "Wretch"],
            Rarity.UNCOMMON: ["Gremlin", "Hob", "Kobold"],
            Rarity.RARE: ["Orc", "Troll", "Ogre"],
            Rarity.LEGENDARY: ["War-Brute", "Iron-Blight", "Chaos-Titan"]
        },
        SpiritType.RESTLESS: {
            Rarity.COMMON: ["Wisp", "Shade", "Flicker"],
            Rarity.UNCOMMON: ["Spirit", "Apparition", "Haunt"],
            Rarity.RARE: ["Specter", "Phantom", "Banshee"],
            Rarity.LEGENDARY: ["Wraith-Lord", "Veil-Revenant", "Death-Echo"]
        }
    }

    @staticmethod
    def generate_familiar_name(spirit_type: SpiritType, essence_type: EssenceType, rarity: Rarity) -> str:
        """Generates a dynamic name for a new familiar."""
        adj = random.choice(NamingRules.ESSENCE_ADJECTIVES[essence_type][rarity])
        noun = random.choice(NamingRules.SPIRIT_NOUNS[spirit_type][rarity])
        return f"{adj} {noun}"
