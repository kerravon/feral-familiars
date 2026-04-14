import asyncio
import random
import discord
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from bot.db import AsyncSessionLocal
from bot.services.encounter_service import EncounterService
from bot.ui.embeds import EmbedFactory
from bot.domain.enums import EncounterType, EssenceType, SpiritType, Rarity
from bot.domain.constants import GameRules, AssetUrls

logger = logging.getLogger("FeralFamiliars")

class SurgeService:
    @staticmethod
    async def trigger_spirit_surge(bot, channel_id, guild_id, releaser_id, subtype, rarity):
        """Spawns 3 random essences after spirit release."""
        await asyncio.sleep(2)
        
        for i in range(3):
            etype = random.choice(list(EssenceType))
            await SurgeService._spawn_with_announcement(
                bot, channel_id, guild_id, EncounterType.ESSENCE, etype.value, None, releaser_id,
                f"✨ Resonance Surge: An essence has materialized! ({i+1}/3)"
            )
            await asyncio.sleep(5)

    @staticmethod
    async def trigger_familiar_surge(bot, channel_id, guild_id, releaser_id, stype, srarity, etype):
        """Spawns the original spirit + 5 random essences."""
        await asyncio.sleep(2)
        
        # 1. Spawn the spirit
        await SurgeService._spawn_with_announcement(
            bot, channel_id, guild_id, EncounterType.SPIRIT, stype.value, srarity, releaser_id,
            "🕊️ Prismatic Surge: The released spirit lingers for a moment!"
        )
        await asyncio.sleep(6)

        # 2. Spawn 5 random essences
        for i in range(5):
            rand_etype = random.choice(list(EssenceType))
            await SurgeService._spawn_with_announcement(
                bot, channel_id, guild_id, EncounterType.ESSENCE, rand_etype.value, None, releaser_id,
                f"✨ Prismatic Burst: An essence has materialized! ({i+1}/5)"
            )
            await asyncio.sleep(5)

    @staticmethod
    async def trigger_well_of_souls_surge(bot, channel_id, guild_id):
        """Spawns 8 items when the pot overflows."""
        channel = bot.get_channel(channel_id)
        if not channel:
            channel = await bot.fetch_channel(channel_id)
            
        await channel.send("🌌 **THE WELL OF SOULS OVERFLOWS!** 🌌\nA massive surge of energy is returning to the world! Get ready!")
        await asyncio.sleep(5)
        
        for i in range(GameRules.PRISMATIC_SURGE_COUNT):
            is_spirit = random.random() < 0.3
            etype = random.choice(list(EssenceType))
            stype = random.choice(list(SpiritType))
            rarity = random.choice(list(Rarity)) if is_spirit else None
            
            await SurgeService._spawn_with_announcement(
                bot, channel_id, guild_id, 
                EncounterType.SPIRIT if is_spirit else EncounterType.ESSENCE, 
                stype.value if is_spirit else etype.value, 
                rarity, 
                None,
                f"🌟 **SURGE EVENT**: Item {i+1}/{GameRules.PRISMATIC_SURGE_COUNT} has manifested!"
            )
            await asyncio.sleep(4)
        
        await channel.send("✨ The energy from the Well has stabilized. Until next time...")

    @staticmethod
    async def _spawn_with_announcement(bot, channel_id, guild_id, type, subtype, rarity, releaser_id, announcement):
        async with AsyncSessionLocal() as session:
            encounter = await EncounterService.spawn_encounter(
                session, channel_id, guild_id, type, 
                override_subtype=subtype, 
                override_rarity=rarity,
                blacklisted_user_id=releaser_id
            )
            
            if encounter:
                # COMMIT the spawn here because it's a standalone background task
                await session.commit()
                
                channel = bot.get_channel(channel_id)
                if not channel: channel = await bot.fetch_channel(channel_id)

                # Use Factory for consistent visuals
                embed = EmbedFactory.create_encounter_embed(encounter, is_lured=True) # Surge items look "lured" (gold color)
                embed.title = announcement # Override title with surge-specific announcement
                
                msg = await channel.send(embed=embed)
                encounter.message_id = msg.id
                await session.commit()
            else:
                logger.warning(f"Surge failed to spawn {type} in {channel_id} - channel busy.")
