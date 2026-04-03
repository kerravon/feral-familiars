import argparse

BASE_STYLE = (
    "stylized cartoon fantasy with subtle gothic undertones, clean simple shapes, smooth lines, "
    "bright but slightly muted color palette, soft gradients, gentle glow effects, centered composition, "
    "single subject, no background, transparent background, isolated subject, high contrast lighting, "
    "crisp edges, bold readable silhouette, minimal detail, icon-like, game asset, readable at small size, "
    "polished illustration, faint magical particles, slightly eerie mystical atmosphere, clean alpha-friendly edges"
)

SPIRIT_FLAVORS = {
    "Feline": (
        "a small stylized feline familiar, sleek body, pointed ears, long tail, agile posture, "
        "glowing eyes, clean readable silhouette"
    ),
    "Canine": (
        "a small stylized canine familiar, alert ears, short snout, sturdy chest, grounded stance, "
        "glowing eyes, clean readable silhouette"
    ),
    "Winged": (
        "a small stylized winged familiar, compact body, simple wings, light hovering posture, "
        "glowing eyes, clean readable silhouette"
    ),
    "Goblin": (
        "a small stylized goblin familiar, hunched posture, oversized ears, short limbs, "
        "mischievous glowing eyes, clean readable silhouette"
    ),
    "Restless": (
        "a small stylized ghost familiar, rounded upper body with trailing mist tail, softly glowing eyes, "
        "gently floating form, clean readable silhouette"
    ),
}

RARITY_FLAVORS = {
    "common": (
        "simple form, minimal ornament, soft glow, clear silhouette"
    ),
    "uncommon": (
        "slightly more defined features, subtle magical markings, gentle pulsing aura"
    ),
    "rare": (
        "refined shape, brighter magical accents, small floating energy fragments, more striking presence"
    ),
    "legendary": (
        "highly refined silhouette, strong glow accents, elegant magical ornament, powerful but clean iconic presence"
    ),
}

ESSENCE_FLAVORS = {
    "Earth": (
        "earth-infused, muted brown and green tones, subtle stone-like markings, faint glowing cracks, "
        "grounded and sturdy presence"
    ),
    "Wind": (
        "wind-infused, pale blue and grey tones, soft flowing wisps trailing from the body, "
        "light and airy motion"
    ),
    "Fire": (
        "fire-infused, warm orange and red tones, soft inner glow, small ember particles, "
        "lively flickering accents"
    ),
    "Water": (
        "water-infused, cool blue tones, smooth glossy highlights, soft droplet-like accents, "
        "calm fluid presence"
    ),
    "Arcane": (
        "arcane-infused, purple and blue tones, soft magical glow, faint rune-like markings, "
        "mysterious magical presence"
    ),
}

# Optional flavor words from your matrix, grouped by essence and rarity.
ADJECTIVE_MATRIX = {
    "Earth": {
        "common": ["Mossy", "Stoney", "Rooted"],
        "uncommon": ["Granite", "Verdant", "Thistled"],
        "rare": ["Ancient", "Lithic", "Overgrown"],
        "legendary": ["World-Born", "Terra-Core", "Tectonic"],
    },
    "Wind": {
        "common": ["Breezy", "Airy", "Drafty"],
        "uncommon": ["Gale-Force", "Swifty", "Whistling"],
        "rare": ["Cyclone", "Sky-Tied", "Zephyr"],
        "legendary": ["Aether-Born", "Zenith", "Storm-Chosen"],
    },
    "Fire": {
        "common": ["Warm", "Flickering", "Glowing"],
        "uncommon": ["Burning", "Ember", "Singeing"],
        "rare": ["Cinder", "Blazing", "Scorch"],
        "legendary": ["Solar-Infused", "Inferno", "Core-Fire"],
    },
    "Arcane": {
        "common": ["Mystic", "Dim", "Strange"],
        "uncommon": ["Rune-Bound", "Eldritch", "Sparking"],
        "rare": ["Celestial", "Astral", "Aetheric"],
        "legendary": ["Void-Touched", "Infinite", "Reality-Warper"],
    },
    "Water": {
        "common": ["Damp", "Fluid", "Mist-Touched"],
        "uncommon": ["Tidal", "Surge", "Bubbling"],
        "rare": ["Wave-Born", "Torrential", "Deep-Sea"],
        "legendary": ["Oceanic", "Abyss-Dredged", "Abyssal"],
    },
}

ADJECTIVE_VISUALS = {
    "Mossy": "soft moss-like patches along the body",
    "Stoney": "heavier stone-like patterning",
    "Rooted": "subtle root-like lines woven through the form",
    "Granite": "denser rocky markings and a heavier build",
    "Verdant": "faint leaf-green accents and natural growth-like details",
    "Thistled": "small thorn-like shapes and sharp natural accents",
    "Ancient": "weathered magical markings suggesting age",
    "Lithic": "layered rock-like textures and carved stone accents",
    "Overgrown": "natural overgrowth motifs wrapping around the form",
    "World-Born": "deep primal earth glow and ancient monumental presence",
    "Terra-Core": "a stronger glowing core with tectonic crack patterns",
    "Tectonic": "bold split-like markings suggesting shifting stone plates",

    "Breezy": "soft light wind trails and airy motion",
    "Airy": "light delicate wisps surrounding the form",
    "Drafty": "thin drifting currents wrapping around the body",
    "Gale-Force": "stronger sweeping wind arcs and energetic motion",
    "Swifty": "faster motion lines and nimble flowing accents",
    "Whistling": "thin curved wind ribbons with a lively magical feel",
    "Cyclone": "spiraling wind patterns concentrated around the body",
    "Sky-Tied": "open airy glow with high, floating energy",
    "Zephyr": "graceful flowing motion and elegant air currents",
    "Aether-Born": "radiant sky-infused energy with elevated presence",
    "Zenith": "bright uplifted glow and poised aerial power",
    "Storm-Chosen": "charged wind energy and stronger atmospheric intensity",

    "Warm": "gentle warmth and a mild ember glow",
    "Flickering": "unstable flickering light across the form",
    "Glowing": "a brighter internal glow and vivid highlights",
    "Burning": "stronger flame-like accents and brighter heat",
    "Ember": "small ember flecks drifting from the body",
    "Singeing": "heated edges with a slightly scorched look",
    "Cinder": "ashy accents and darker ember tones",
    "Blazing": "brighter flame energy and stronger glow",
    "Scorch": "darker heated markings and intense highlights",
    "Solar-Infused": "radiant fire energy with a noble bright core",
    "Inferno": "intense internal fire glow and dominant heat aura",
    "Core-Fire": "a concentrated molten core effect and powerful glow",

    "Mystic": "soft mysterious magical shimmer",
    "Dim": "subdued magical glow with restrained energy",
    "Strange": "slightly unusual magical patterns and eerie accents",
    "Rune-Bound": "clear rune-like markings across the body",
    "Eldritch": "odd arcane shapes and unsettling magical distortion",
    "Sparking": "small magical sparks dancing around the form",
    "Celestial": "star-like highlights and refined arcane glow",
    "Astral": "soft cosmic energy accents and distant light patterns",
    "Aetheric": "lightweight magical energy with elegant flowing runes",
    "Void-Touched": "darker arcane glow with mysterious depth",
    "Infinite": "layered magical energy suggesting endless power",
    "Reality-Warper": "subtle distortion effects and unstable magical geometry",

    "Damp": "soft moisture sheen and gentle water highlights",
    "Fluid": "smooth flowing contours and liquid motion",
    "Mist-Touched": "light mist curling around the body",
    "Tidal": "stronger wave-like accents and rolling motion",
    "Surge": "energetic water flow patterns and brighter highlights",
    "Bubbling": "small bubbles and lively liquid details",
    "Wave-Born": "broader water arcs and ocean-like motion",
    "Torrential": "heavier flowing energy and forceful liquid accents",
    "Deep-Sea": "darker blue tones and deeper aquatic glow",
    "Oceanic": "broad rich water energy and expansive flow",
    "Abyss-Dredged": "deep dark aquatic tones with eerie glow",
    "Abyssal": "mysterious deep-water presence and shadowed fluid energy",
}

def get_adjective_visual(essence: str, rarity: str, adjective: str | None) -> str:
    if adjective:
        return ADJECTIVE_VISUALS.get(adjective, "")
    return ""

def suggest_adjectives(essence: str, rarity: str) -> list[str]:
    return ADJECTIVE_MATRIX.get(essence, {}).get(rarity, [])

def generate_prompt(spirit: str, rarity: str, essence: str, adjective: str | None = None) -> str:
    spirit = spirit.title()
    rarity = rarity.lower()
    essence = essence.title()

    s_text = SPIRIT_FLAVORS.get(spirit, "a small stylized mysterious familiar, clean readable silhouette")
    r_text = RARITY_FLAVORS.get(rarity, "")
    e_text = ESSENCE_FLAVORS.get(essence, "")
    a_text = get_adjective_visual(essence, rarity, adjective)

    parts = [BASE_STYLE, s_text, r_text, e_text]
    if a_text:
        parts.append(a_text)

    return ", ".join(part for part in parts if part)

def main():
    parser = argparse.ArgumentParser(description="Generate image prompts for Feral Familiar familiars.")
    parser.add_argument("--spirit", choices=list(SPIRIT_FLAVORS.keys()), required=True)
    parser.add_argument("--rarity", choices=list(RARITY_FLAVORS.keys()), required=True)
    parser.add_argument("--essence", choices=list(ESSENCE_FLAVORS.keys()), required=True)
    parser.add_argument(
        "--adjective",
        required=False,
        help="Optional adjective from your matrix, e.g. Mossy, Ember, Zephyr, Abyssal",
    )
    parser.add_argument(
        "--show-adjectives",
        action="store_true",
        help="Show valid adjective suggestions for the chosen essence and rarity",
    )

    args = parser.parse_args()

    if args.show_adjectives:
        options = suggest_adjectives(args.essence.title(), args.rarity.lower())
        print("\nSuggested adjectives:")
        for item in options:
            print(f"- {item}")
        print()

    prompt = generate_prompt(args.spirit, args.rarity, args.essence, args.adjective)

    print("\n" + "=" * 20 + " GENERATED PROMPT " + "=" * 20)
    label_parts = [args.rarity.upper()]
    if args.adjective:
        label_parts.append(args.adjective)
    label_parts.extend([args.essence.title(), args.spirit.title()])
    print(f"\nTarget: {' '.join(label_parts)}")
    print("\n" + prompt)
    print("\n" + "=" * 58 + "\n")

if __name__ == "__main__":
    main()
