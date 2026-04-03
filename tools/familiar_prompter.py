import argparse

BASE_STYLE = (
    "stylized cartoon fantasy with subtle gothic undertones, clean simple shapes, smooth lines, "
    "bright but slightly muted color palette, soft gradients, gentle glow effects, centered composition, "
    "single subject, minimal background, dark soft backdrop for contrast, high contrast lighting, "
    "crisp edges, bold readable silhouette, minimal detail, icon-like, game asset, readable at small size, "
    "polished illustration, faint magical particles, slightly eerie mystical atmosphere, "
    "body made of flowing energy, partially dissolving into light particles, hovering and unstable silhouette, "
    "transparent image"
)

SPIRIT_FLAVORS = {
    "Feline": "a sleek predatory feline with glowing eyes and agile posture, sharp ears, flowing spectral tail",
    "Canine": "a powerful spectral canine, thick mane of energy, alert pointed ears, sturdy broad chest",
    "Winged": "a drifting spectral bird form with faint wing-like shapes extending outward, feathers loosely suggested",
    "Goblin": "a small hunched impish figure, oversized pointed ears, long thin limbs, glowing mischievous eyes",
    "Restless": "a ghostly amorphous wisp-like entity, drifting veils of mist, a skull-like essence visible in the core"
}

RARITY_FLAVORS = {
    "common": "raw and simple form, no ornamentation, pure elemental energy",
    "uncommon": "more defined features, gentle pulsing aura, small magical runes glowing on its body",
    "rare": "adorned with ancient stone ornaments, intense crackling energy, floating magical shards surrounding it",
    "legendary": "wearing intricate mythical gold armor, radiating massive divine power, colossal ethereal presence, complex energy wings"
}

ESSENCE_FLAVORS = {
    "Earth": "infused with mossy granite, cracked stone skin, green leafy particles, grounded and heavy",
    "Wind": "swirling with high-velocity air, translucent misty body, fast whistling wind trails, light blue and white",
    "Fire": "body of molten lava and flickering flames, intense orange and red glow, rising smoke and embers",
    "Water": "composed of flowing liquid and crashing waves, deep blue crystalline core, splashing droplets and bubbles",
    "Arcane": "shimmering purple void energy, rune-etched skin, stars and galaxies visible within its form, stable eldritch power"
}

def generate_prompt(spirit, rarity, essence):
    spirit = spirit.title()
    rarity = rarity.lower()
    essence = essence.title()

    s_text = SPIRIT_FLAVORS.get(spirit, "a mysterious entity")
    r_text = RARITY_FLAVORS.get(rarity, "")
    e_text = ESSENCE_FLAVORS.get(essence, "")

    full_prompt = f"{BASE_STYLE}, {s_text}, {r_text}, {e_text}"
    return full_prompt

def main():
    parser = argparse.ArgumentParser(description="Generate image prompts for Feral Familiars.")
    parser.add_argument("--spirit", choices=list(SPIRIT_FLAVORS.keys()), required=True)
    parser.add_argument("--rarity", choices=list(RARITY_FLAVORS.keys()), required=True)
    parser.add_argument("--essence", choices=list(ESSENCE_FLAVORS.keys()), required=True)

    args = parser.parse_args()

    prompt = generate_prompt(args.spirit, args.rarity, args.essence)
    
    print("\n" + "="*20 + " GENERATED PROMPT " + "="*20)
    print(f"\nTarget: {args.rarity.upper()} {args.essence} {args.spirit}")
    print("\n" + prompt)
    print("\n" + "="*58 + "\n")

if __name__ == "__main__":
    main()
