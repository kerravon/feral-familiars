import discord
from bot.domain.enums import EncounterType, EssenceType, SpiritType, Rarity, ResonanceMode
from bot.domain.constants import AssetUrls, GameRules
from bot.models.encounter import Encounter
from bot.models.familiar import Familiar

class EmbedFactory:
    @staticmethod
    def create_encounter_embed(encounter: Encounter, is_lured: bool = False):
        title = f"A {encounter.subtype} {encounter.type.value.title()} has appeared!"
        if is_lured:
            title = f"✨ INCENSE: {title}"
        
        color = discord.Color.gold() if is_lured else (discord.Color.blue() if encounter.type == EncounterType.ESSENCE else discord.Color.purple())
        
        embed = discord.Embed(
            title=title,
            description=f"Type `bind` to capture this {encounter.type.value}." if encounter.type == EncounterType.ESSENCE else f"Type `bind spirit` to capture this spirit!",
            color=color
        )
        
        if encounter.type == EncounterType.ESSENCE:
            embed.set_image(url=AssetUrls.ESSENCE_IMAGES.get(EssenceType(encounter.subtype)))
        else:
            embed.set_image(url=AssetUrls.SPIRIT_IMAGES.get(SpiritType(encounter.subtype)))
        
        if encounter.rarity:
            embed.add_field(name="Rarity", value=encounter.rarity.value.upper())
        
        if getattr(encounter, "_temp_anchor_active", False):
            embed.set_footer(text="✨ Temporal Anchor Active: Spawns stay 15s longer!")
            
        return embed

    @staticmethod
    def create_capture_success_embed(encounter: Encounter, user_name: str):
        embed = discord.Embed(
            title=f"Captured by {user_name}!",
            description=f"The {encounter.subtype} {encounter.type.value} has been bound.",
            color=discord.Color.green()
        )
        
        if encounter.type == EncounterType.ESSENCE:
            url = AssetUrls.BOUND_IMAGES.get(EssenceType(encounter.subtype))
        else:
            url = AssetUrls.SPIRIT_BOUND_IMAGES.get(SpiritType(encounter.subtype))
            
        if url:
            embed.set_image(url=url)
            
        if encounter.rarity:
            embed.add_field(name="Rarity", value=encounter.rarity.value.upper())
            
        return embed

    @staticmethod
    def create_familiar_card(f: Familiar, current_time):
        embed = discord.Embed(title=f"🐾 {f.name}", color=discord.Color.gold())
        embed.add_field(name="Type", value=f"{f.spirit_type.value} / {f.essence_type.value}", inline=True)
        embed.add_field(name="Rarity", value=f.rarity.value.title(), inline=True)
        embed.add_field(name="Level", value=f"**Lv. {f.level}** / {GameRules.MAX_LEVEL}", inline=True)
        
        # XP Bar
        xp_needed = GameRules.XP_CURVE.get(f.level, 0)
        if xp_needed > 0:
            progress = (f.xp / xp_needed) * 100
            filled = int(progress / 10)
            bar = "🟦" * filled + "⬛" * (10 - filled)
            embed.add_field(name="Experience", value=f"{bar} {f.xp}/{xp_needed} XP ({progress:.1f}%)", inline=False)
        else:
            embed.add_field(name="Experience", value="🌟 **MAX LEVEL**", inline=False)

        status = "💤 Inactive"
        if f.active_until and current_time < f.active_until:
            delta = f.active_until - current_time
            mins = int(delta.total_seconds() / 60)
            status = f"🔥 RESONATING ({mins}m left)"
        embed.add_field(name="Resonance Status", value=status, inline=False)

        # Passive
        base_chance = GameRules.BASE_PASSIVE_CHANCE.get(f.rarity, 0.08)
        if f.essence_type == EssenceType.ARCANE: base_chance += GameRules.ARCANE_PASSIVE_BONUS
        
        total_chance = (base_chance + f.growth_bonus) * 100

        mode_info = {
            ResonanceMode.ECHO: "**ECHO:** 2x chance for same element.",
            ResonanceMode.PULSE: "**PULSE:** Chance for a RANDOM element.",
            ResonanceMode.ATTRACT: f"**ATTRACT:** Attracts **{(f.attract_element or EssenceType.ARCANE).value}** essence."
        }
        mode_desc = mode_info.get(f.resonance_mode, "Unknown Mode")
        passive_desc = f"{mode_desc}\n**Trigger Chance:** {total_chance:.1f}% ({base_chance*100:.0f}% base + {f.growth_bonus*100:.1f}% growth)"

        embed.add_field(name=f"Passive Power ({f.resonance_mode.value.upper()})", value=passive_desc, inline=False)
        return embed

    @staticmethod
    def create_level_up_embed(familiar_name: str, level: int, roll: float, unlocks: list):
        unlock_text = "\n".join([f"✨ **Unlocked:** {u}" for u in unlocks])
        embed = discord.Embed(
            title=f"🌟 LEVEL UP: {familiar_name}!",
            description=f"Your familiar has reached **Level {level}**!\n\n"
                        f"📈 **Growth Roll:** +{roll:.2%}\n"
                        f"{unlock_text}",
            color=discord.Color.gold()
        )
        return embed
