from bot.domain.enums import EssenceType, SpiritType, Rarity, EncounterType, ResonanceMode

class GameRules:
    # --- Spawning ---
    SPAWN_CHANCE_BASE = 25  # %
    ACTIVITY_BONUS_PER_MSG = 0.5 # %
    ACTIVITY_BONUS_MAX = 20 # %
    PITY_BONUS_PER_FAILED_TICK = 2 # %
    
    ESSENCE_WEIGHTS = {
        EssenceType.EARTH: 22,
        EssenceType.WIND: 22,
        EssenceType.FIRE: 22,
        EssenceType.ARCANE: 12,
        EssenceType.WATER: 22
    }
    
    SPIRIT_WEIGHTS = {
        SpiritType.FELINE: 22.5,
        SpiritType.CANINE: 22.5,
        SpiritType.WINGED: 22.5,
        SpiritType.GOBLIN: 22.5,
        SpiritType.RESTLESS: 10.0
    }

    RARITY_WEIGHTS = {
        Rarity.COMMON: 0.60,
        Rarity.UNCOMMON: 0.25,
        Rarity.RARE: 0.12,
        Rarity.LEGENDARY: 0.03
    }

    # --- Rituals ---
    RITUAL_COSTS = {
        Rarity.COMMON: 10,
        Rarity.UNCOMMON: 20,
        Rarity.RARE: 40,
        Rarity.LEGENDARY: 80
    }
    
    RESTLESS_ARCANE_COSTS = {
        Rarity.COMMON: 5,
        Rarity.UNCOMMON: 10,
        Rarity.RARE: 15,
        Rarity.LEGENDARY: 25
    }

    # --- Leveling & XP ---
    MAX_LEVEL = 10
    XP_CURVE = {
        1: 100, 2: 200, 3: 300, 4: 500, 5: 750,
        6: 1000, 7: 1500, 8: 2500, 9: 4000, 10: 0
    }
    
    XP_PER_CAPTURE = 5
    XP_PER_MATCHING_CAPTURE = 10
    
    XP_PER_FEED_MATCHING = 10
    XP_PER_FEED_ARCANE = 20
    XP_PER_FEED_OTHER = 2
    
    # --- Passives ---
    BASE_PASSIVE_CHANCE = {
        Rarity.COMMON: 0.08,
        Rarity.UNCOMMON: 0.15,
        Rarity.RARE: 0.25,
        Rarity.LEGENDARY: 0.40
    }
    
    ARCANE_PASSIVE_BONUS = 0.10
    GROWTH_ROLL_RANGE = (0.005, 0.020) # 0.5% to 2.0% per level
    
    UNLOCK_PULSE_LEVEL = 5
    UNLOCK_ATTRACT_LEVEL = 8
    
    # --- Social & Taxes ---
    SOCIAL_TAX_PERCENT = 0.03 # 3%
    WELL_OF_SOULS_THRESHOLD = 1000
    PRISMATIC_SURGE_COUNT = 8

    SPIRIT_TAX_MAP = {
        Rarity.COMMON: 2,
        Rarity.UNCOMMON: 5,
        Rarity.RARE: 10,
        Rarity.LEGENDARY: 25
    }

class AssetUrls:
    # In a future refactor, these could move to a DB or JSON
    FADED_IMAGE = "https://i.ibb.co/NR7brt7/faded.webp"
    
    ESSENCE_IMAGES = {
        EssenceType.EARTH: "https://i.ibb.co/vCpGNdMt/earth-essence.webp",
        EssenceType.WIND: "https://i.ibb.co/gb3RfzWM/wind-essence.webp",
        EssenceType.FIRE: "https://i.ibb.co/rGGztGCk/fire-essence.webp",
        EssenceType.ARCANE: "https://i.ibb.co/qLJyg17w/arcane-essence.webp",
        EssenceType.WATER: "https://i.ibb.co/wFFV89H0/water-essence.webp"
    }

    BOUND_IMAGES = {
        EssenceType.EARTH: "https://i.ibb.co/bjqh1k1Y/earth-essence-bound.webp",
        EssenceType.WIND: "https://i.ibb.co/DHX9sJx0/wind-essence-bound.webp",
        EssenceType.FIRE: "https://i.ibb.co/8n8CLp4Z/fire-essence-bound.webp",
        EssenceType.ARCANE: "https://i.ibb.co/DPY5GgZ2/arcane-essence-bound.webp",
        EssenceType.WATER: "https://i.ibb.co/0VjcZH9N/water-essence-bound.webp"
    }

    SPIRIT_IMAGES = {
        SpiritType.FELINE: "https://i.ibb.co/wZM4kYPf/air-essence2.png",
        SpiritType.CANINE: "https://i.ibb.co/cSdQpdBq/canine-spirit.webp",
        SpiritType.WINGED: "https://i.ibb.co/Vpt1wK9T/winged-spirit.webp",
        SpiritType.GOBLIN: "https://i.ibb.co/gL9CWVKP/goblin-spirit.webp",
        SpiritType.RESTLESS: "https://i.ibb.co/mCvQ1LHH/restless-spirit.webp"
    }

    SPIRIT_BOUND_IMAGES = {
        SpiritType.FELINE: "https://i.ibb.co/S4w3K1Tg/air-essence-bound2.png",
        SpiritType.CANINE: "https://i.ibb.co/600vcDKf/canine-spirit-bound.webp",
        SpiritType.WINGED: "https://i.ibb.co/j9dpkPYF/winged-spirit-bound.webp",
        SpiritType.GOBLIN: "https://i.ibb.co/Csp2yHNc/goblin-spirit-bound.webp",
        SpiritType.RESTLESS: "https://i.ibb.co/jvpcjZkt/restless-spirit-bound.webp"
    }
