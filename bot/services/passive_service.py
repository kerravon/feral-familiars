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

        # Chance based on rarity (Common: 10%, Uncommon: 15%, Rare: 20%, Legendary: 30%)
        chance_map = {
            GameConstants.COMMON: 0.10,
            GameConstants.UNCOMMON: 0.15,
            GameConstants.RARE: 0.20,
            GameConstants.LEGENDARY: 0.30
        }
        
        chance = chance_map.get(familiar.rarity, 0.10)
        if random.random() > chance:
            return None

        # Determine effect based on Essence type
        # Earth -> Extra quantity (+1)
        # Wind -> (For MVP, we'll just do extra quantity as well)
        # Fire -> Random extra essence
        # Arcane -> Duplicate
        
        effect_msg = ""
        if familiar.essence_type == GameConstants.EARTH:
            # Add 1 extra essence
            stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == captured_type)
            res = await session.execute(stmt)
            ess = res.scalar_one()
            ess.count += 1
            effect_msg = f"🌿 **{familiar.name}**'s Earth bond found an extra {captured_type} essence!"
        
        elif familiar.essence_type == GameConstants.ARCANE:
            # Duplicate
            stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == captured_type)
            res = await session.execute(stmt)
            ess = res.scalar_one()
            ess.count += 1
            effect_msg = f"✨ **{familiar.name}**'s Arcane resonance duplicated the {captured_type} essence!"
            
        elif familiar.essence_type == GameConstants.FIRE:
            # Random extra essence
            rand_type = random.choice(GameConstants.ESSENCES)
            stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == rand_type)
            res = await session.execute(stmt)
            ess = res.scalar_one_or_none()
            if not ess:
                ess = Essence(user_id=user_id, type=rand_type, count=1)
                session.add(ess)
            else:
                ess.count += 1
            effect_msg = f"🔥 **{familiar.name}**'s Cinder sparked a new {rand_type} essence!"
        
        elif familiar.essence_type == GameConstants.WATER:
            # Random different essence (Growth/Flow)
            other_types = [e for e in GameConstants.ESSENCES if e != captured_type]
            rand_type = random.choice(other_types)
            stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == rand_type)
            res = await session.execute(stmt)
            ess = res.scalar_one_or_none()
            if not ess:
                ess = Essence(user_id=user_id, type=rand_type, count=1)
                session.add(ess)
            else:
                ess.count += 1
            effect_msg = f"🌊 **{familiar.name}**'s Fluidity flowed into a {rand_type} essence!"
        
        else: # WIND
            effect_msg = f"💨 **{familiar.name}**'s Swiftness gathered the essence instantly (Passive triggered but effect TBD)!"

        await session.commit()
        return effect_msg
