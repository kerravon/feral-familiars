import random
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from bot.models.familiar import Familiar

logger = logging.getLogger("FeralFamiliars")

class LevelingService:
    # XP required to reach the NEXT level
    XP_CURVE = {
        1: 100,
        2: 200,
        3: 300,
        4: 500,
        5: 750,
        6: 1000,
        7: 1500,
        8: 2500,
        9: 4000,
        10: 0 # Max level
    }

    @staticmethod
    async def add_xp(session: AsyncSession, familiar: Familiar, amount: int):
        """Adds XP and handles potential level ups."""
        if familiar.level >= 10:
            return []

        familiar.xp += amount
        level_up_events = []

        while True:
            xp_needed = LevelingService.XP_CURVE.get(familiar.level, 0)
            if xp_needed == 0: # Max level reached
                familiar.xp = 0
                break
            
            if familiar.xp >= xp_needed:
                familiar.xp -= xp_needed
                event = await LevelingService._level_up(session, familiar)
                level_up_events.append(event)
            else:
                break
        
        await session.commit()
        return level_up_events

    @staticmethod
    async def _level_up(session: AsyncSession, familiar: Familiar):
        """Internal logic for a single level gain."""
        familiar.level += 1
        
        # RNG Growth Roll: +0.5% to +2.0%
        roll = random.uniform(0.005, 0.020)
        familiar.growth_bonus += roll
        
        unlocks = []
        if familiar.level == 5:
            unlocks.append("PULSE Resonance Mode")
        if familiar.level == 8:
            unlocks.append("ATTRACT Resonance Mode")
        if familiar.level == 10:
            unlocks.append("MAX LEVEL REACHED!")

        logger.info(f"Familiar {familiar.name} (ID: {familiar.id}) leveled up to {familiar.level}. Roll: +{roll:.2%}")
        
        return {
            "level": familiar.level,
            "roll": roll,
            "unlocks": unlocks
        }
