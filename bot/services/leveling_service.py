import random
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from bot.models.familiar import Familiar
from bot.domain.constants import GameRules

logger = logging.getLogger("FeralFamiliars")

class LevelingService:
    @staticmethod
    async def add_xp(session: AsyncSession, familiar: Familiar, amount: int):
        """Adds XP and handles potential level ups. Does NOT commit."""
        if familiar.level >= GameRules.MAX_LEVEL:
            return []

        familiar.xp += amount
        level_up_events = []

        while True:
            xp_needed = GameRules.XP_CURVE.get(familiar.level, 0)
            if xp_needed == 0: # Max level reached
                familiar.xp = 0
                break
            
            if familiar.xp >= xp_needed:
                familiar.xp -= xp_needed
                event = await LevelingService._level_up(session, familiar)
                level_up_events.append(event)
            else:
                break
        
        return level_up_events

    @staticmethod
    async def _level_up(session: AsyncSession, familiar: Familiar):
        """Internal logic for a single level gain. Does NOT commit."""
        familiar.level += 1
        
        # RNG Growth Roll
        roll = random.uniform(*GameRules.GROWTH_ROLL_RANGE)
        familiar.growth_bonus += roll
        
        unlocks = []
        if familiar.level == GameRules.UNLOCK_PULSE_LEVEL:
            unlocks.append("PULSE Resonance Mode")
        if familiar.level == GameRules.UNLOCK_ATTRACT_LEVEL:
            unlocks.append("ATTRACT Resonance Mode")
        if familiar.level == GameRules.MAX_LEVEL:
            unlocks.append("MAX LEVEL REACHED!")

        logger.info(f"Familiar {familiar.name} (ID: {familiar.id}) leveled up to {familiar.level}. Roll: +{roll:.2%}")
        
        return {
            "name": familiar.name,
            "level": familiar.level,
            "roll": roll,
            "unlocks": unlocks
        }
