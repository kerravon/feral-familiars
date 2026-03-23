class GameConstants:
    # Essence Types
    EARTH = "Earth"
    WIND = "Wind"
    FIRE = "Fire"
    ARCANE = "Arcane"
    WATER = "Water"
    ESSENCES = [EARTH, WIND, FIRE, ARCANE, WATER]

    # Spirit Types
    FELINE = "Feline"
    CANINE = "Canine"
    WINGED = "Winged"
    GOBLIN = "Goblin"
    SPIRITS = [FELINE, CANINE, WINGED, GOBLIN]

    # Rarities
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"
    RARITIES = [COMMON, UNCOMMON, RARE, LEGENDARY]

    # Costs (Fixed requirements for MVP)
    COST_MAP = {
        COMMON: 10,
        UNCOMMON: 20,
        RARE: 40,
        LEGENDARY: 80
    }

    # Essence Images (URLs)
    ESSENCE_IMAGES = {
        EARTH: "https://i.ibb.co/ymH9mNXJ/earth-essence.png",
        WIND: "https://i.ibb.co/wZM4kYPf/air-essence2.png",
        FIRE: "https://i.ibb.co/LXpxBzHZ/fire-essence.png",
        ARCANE: "https://i.ibb.co/8X8v8X8.png", # Still needs an image!
        WATER: "https://i.ibb.co/zTmtRwx1/water-essence.png"
    }

    # Images shown AFTER capture (Bound)
    BOUND_IMAGES = {
        EARTH: "https://i.ibb.co/ymH9mNXJ/earth-essence.png", # Replace with bound versions later!
        WIND: "https://i.ibb.co/S4w3K1Tg/air-essence-bound2.png",
        FIRE: "https://i.ibb.co/LXpxBzHZ/fire-essence.png",
        ARCANE: "https://i.ibb.co/8X8v8X8.png",
        WATER: "https://i.ibb.co/zTmtRwx1/water-essence.png"
    }

    # Word Banks for Dynamic Naming
    ESSENCE_ADJECTIVES = {
        EARTH: {
            COMMON: ["Mossy", "Stoney", "Rooted"],
            UNCOMMON: ["Granite", "Verdant", "Thistled"],
            RARE: ["Ancient", "Lithic", "Overgrown"],
            LEGENDARY: ["World-Born", "Terra-Core", "Tectonic"]
        },
        WIND: {
            COMMON: ["Breezy", "Airy", "Drafty"],
            UNCOMMON: ["Gale-Force", "Swifty", "Whistling"],
            RARE: ["Cyclone", "Sky-Tied", "Zephyr"],
            LEGENDARY: ["Aether-Born", "Zenith", "Storm-Chosen"]
        },
        FIRE: {
            COMMON: ["Warm", "Flickering", "Glowing"],
            UNCOMMON: ["Burning", "Ember", "Singeing"],
            RARE: ["Cinder", "Blazing", "Scorch"],
            LEGENDARY: ["Solar-Infused", "Inferno", "Core-Fire"]
        },
        ARCANE: {
            COMMON: ["Mystic", "Dim", "Strange"],
            UNCOMMON: ["Rune-Bound", "Eldritch", "Sparking"],
            RARE: ["Celestial", "Astral", "Aetheric"],
            LEGENDARY: ["Void-Touched", "Infinite", "Reality-Warper"]
        },
        WATER: {
            COMMON: ["Damp", "Fluid", "Mist-Touched"],
            UNCOMMON: ["Tidal", "Surge", "Bubbling"],
            RARE: ["Wave-Born", "Torrential", "Deep-Sea"],
            LEGENDARY: ["Oceanic", "Abyss-Dredged", "Abyssal"]
        }
    }

    SPIRIT_NOUNS = {
        FELINE: {
            COMMON: ["Cat", "Kitten", "Stray"],
            UNCOMMON: ["Bobcat", "Lynx", "Serval"],
            RARE: ["Cougar", "Panther", "Caracal"],
            LEGENDARY: ["Great-Cat", "Apex-Stalker", "Void-Leopard"]
        },
        CANINE: {
            COMMON: ["Mutt", "Hound", "Pup"],
            UNCOMMON: ["Jackal", "Wolf", "Coyote"],
            RARE: ["Dire-Wolf", "Husky", "Mastiff"],
            LEGENDARY: ["Night-Stalker", "Alpha-Predator", "Storm-Howler"]
        },
        WINGED: {
            COMMON: ["Bird", "Sparrow", "Chick"],
            UNCOMMON: ["Falcon", "Hawk", "Kestrel"],
            RARE: ["Eagle", "Owl", "Vulture"],
            LEGENDARY: ["Cloud-Sovereign", "Sky-Reaper", "Sun-Striker"]
        },
        GOBLIN: {
            COMMON: ["Imp", "Runt", "Wretch"],
            UNCOMMON: ["Gremlin", "Hob", "Kobold"],
            RARE: ["Orc", "Troll", "Ogre"],
            LEGENDARY: ["War-Brute", "Iron-Blight", "Chaos-Titan"]
        }
    }
