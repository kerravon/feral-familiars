from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.familiar import Familiar
from bot.models.essence import Essence
from bot.utils.constants import GameConstants
import random

class PassiveService:
    @staticmethod
    async def get_active_familiar(session: AsyncSession, user_id: int) -> Familiar:
        stmt = select(Familiar).where(Familiar.user_id == user_id, Familiar.is_active == True)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def equip_familiar(session: AsyncSession, user_id: int, familiar_id: int):
        """
        Equips a familiar, ensuring only one is active at a time for the user.
        Returns (success, result_message_or_familiar)
        """
        try:
            # 1. Verify ownership and existence
            stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
            result = await session.execute(stmt)
            familiar = result.scalar_one_or_none()
            
            if not familiar:
                return False, "Familiar not found in your stable."

            async with session.begin_nested():
                # 2. Deactivate current active familiar(s)
                await session.execute(
                    update(Familiar)
                    .where(Familiar.user_id == user_id, Familiar.is_active == True)
                    .values(is_active=False)
                )
                
                # 3. Activate new one
                familiar.is_active = True
            
            await session.commit()
            return True, familiar
        except Exception as e:
            await session.rollback()
            return False, f"Error equipping familiar: {e}"

    @staticmethod
    async def trigger_passive_bonus(session: AsyncSession, user_id: int, captured_type: str):
        familiar = await PassiveService.get_active_familiar(session, user_id)
        if not familiar:
            return None

        # Scaling: Chance based on rarity of the spirit
        # Common: 15%, Uncommon: 25%, Rare: 40%, Legendary: 60%
        chance_map = {
            GameConstants.COMMON: 0.15,
            GameConstants.UNCOMMON: 0.25,
            GameConstants.RARE: 0.40,
            GameConstants.LEGENDARY: 0.60
        }
        
        chance = chance_map.get(familiar.rarity, 0.15)
        
        # Arcane familiars are stronger (+15% flat bonus to trigger)
        if familiar.essence_type == GameConstants.ARCANE:
            chance += 0.15

        if random.random() > chance:
            return None

        # 1. Base Element logic: Double the essence of the SAME type
        # 2. Arcane logic: Double ANY essence type
        can_double = (familiar.essence_type == captured_type) or (familiar.essence_type == GameConstants.ARCANE)

        if not can_double:
            return None

        # Double the essence!
        stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == captured_type)
        res = await session.execute(stmt)
        ess = res.scalar_one()
        ess.count += 1
        
        emoji = "✨" if familiar.essence_type == GameConstants.ARCANE else "🌀"
        effect_msg = f"{emoji} **{familiar.name}**'s resonance duplicated the {captured_type} essence!"
        
        await session.commit()
        return effect_msg
