class GameConstants:
    # Essence Types
    EARTH = "Earth"
    WIND = "Wind"
    FIRE = "Fire"
    ARCANE = "Arcane"
    WATER = "Water"
    ESSENCES = [EARTH, WIND, FIRE, ARCANE, WATER]
    # Weights: Earth, Wind, Fire, Arcane, Water (Base elements equal, Arcane half-rate)
    ESSENCE_WEIGHTS = [22, 22, 22, 12, 22]

    # Spirit Types
    FELINE = "Feline"
    CANINE = "Canine"
    WINGED = "Winged"
    GOBLIN = "Goblin"
    RESTLESS = "Restless"
    SPIRITS = [FELINE, CANINE, WINGED, GOBLIN, RESTLESS]

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
        EARTH: "https://i.ibb.co/vCpGNdMt/earth-essence.webp",
        WIND: "https://i.ibb.co/gb3RfzWM/wind-essence.webp",
        FIRE: "https://i.ibb.co/rGGztGCk/fire-essence.webp",
        ARCANE: "https://i.ibb.co/qLJyg17w/arcane-essence.webp",
        WATER: "https://i.ibb.co/wFFV89H0/water-essence.webp"
    }

    # Images shown AFTER capture (Bound)
    BOUND_IMAGES = {
        EARTH: "https://i.ibb.co/bjqh1k1Y/earth-essence-bound.webp",
        WIND: "https://i.ibb.co/DHX9sJx0/wind-essence-bound.webp",
        FIRE: "https://i.ibb.co/8n8CLp4Z/fire-essence-bound.webp",
        ARCANE: "https://i.ibb.co/DPY5GgZ2/arcane-essence-bound.webp",
        WATER: "https://i.ibb.co/0VjcZH9N/water-essence-bound.webp"
    }

    # Spirit Images
    SPIRIT_IMAGES = {
        FELINE: "https://i.ibb.co/wZM4kYPf/air-essence2.png", # Still need Feline! Reusing air for now
        CANINE: "https://i.ibb.co/cSdQpdBq/canine-spirit.webp",
        WINGED: "https://i.ibb.co/Vpt1wK9T/winged-spirit.webp",
        GOBLIN: "https://i.ibb.co/gL9CWVKP/goblin-spirit.webp",
        RESTLESS: "https://i.ibb.co/mCvQ1LHH/restless-spirit.webp"
    }

    SPIRIT_BOUND_IMAGES = {
        FELINE: "https://i.ibb.co/S4w3K1Tg/air-essence-bound2.png", # Still need Feline!
        CANINE: "https://i.ibb.co/600vcDKf/canine-spirit-bound.webp",
        WINGED: "https://i.ibb.co/j9dpkPYF/winged-spirit-bound.webp",
        GOBLIN: "https://i.ibb.co/Csp2yHNc/goblin-spirit-bound.webp",
        RESTLESS: "https://i.ibb.co/jvpcjZkt/restless-spirit-bound.webp"
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
        },
        RESTLESS: {
            COMMON: ["Wisp", "Shade", "Flicker"],
            UNCOMMON: ["Spirit", "Apparition", "Haunt"],
            RARE: ["Specter", "Phantom", "Banshee"],
            LEGENDARY: ["Wraith-Lord", "Veil-Revenant", "Death-Echo"]
        }
    }
