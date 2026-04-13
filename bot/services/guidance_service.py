import discord
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from bot.models.base import User
import logging

logger = logging.getLogger("FeralFamiliars")

class GuidanceService:
    @staticmethod
    def get_onboarding_embed():
        """Returns the initial onboarding embed for channel activation."""
        embed = discord.Embed(
            title="🌌 The Veil has Thinned!",
            description=(
                "Mystical energies are now manifesting in this channel. "
                "Bind them to begin your journey as a master of spirits."
            ),
            color=discord.Color.purple()
        )
        embed.add_field(
            name="🪢 How to Play",
            value=(
                "1. **Watch for Spawns:** Essences and Spirits appear periodically.\n"
                "2. **Capture:** Type `bind` for essences or `bind spirit` for spirits.\n"
                "3. **Progress:** Use `/ritual` to create companions and `/help` for guidance."
            ),
            inline=False
        )
        embed.set_footer(text="The rhythmic pulse of the world begins now...")
        return embed

    @staticmethod
    async def check_milestone(session: AsyncSession, user_id: int, milestone_type: str):
        """Checks if a user should receive a one-time tip based on their actions."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None

        tip_embed = None
        
        if milestone_type == "essence" and not user.has_seen_essence_tip:
            user.has_seen_essence_tip = True
            tip_embed = discord.Embed(
                title="✨ Your First Essence!",
                description=(
                    "You've bound raw elemental energy. Collect enough matching essences "
                    "to perform a **Ritual** with a captured Spirit.\n\n"
                    "Check your progress with `/inventory`."
                ),
                color=discord.Color.blue()
            )
        
        elif milestone_type == "spirit" and not user.has_seen_spirit_tip:
            user.has_seen_spirit_tip = True
            tip_embed = discord.Embed(
                title="👻 A Spirit is Bound!",
                description=(
                    "You have captured a mystical entity. To give it form, use the "
                    "**/ritual** command. You will need matching essences to complete the binding."
                ),
                color=discord.Color.purple()
            )
            
        elif milestone_type == "familiar" and not user.has_seen_familiar_tip:
            user.has_seen_familiar_tip = True
            tip_embed = discord.Embed(
                title="🐾 A Familiar is Born!",
                description=(
                    "Your companion is ready! Use **/summon** to make it active, "
                    "then use **/familiar** to **Ignite Resonance** and unlock its passive powers."
                ),
                color=discord.Color.gold()
            )

        if tip_embed:
            await session.commit()
            tip_embed.set_footer(text="Tip: Use /help at any time for detailed information.")
            return tip_embed
            
        return None
