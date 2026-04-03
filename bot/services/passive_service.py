from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.familiar import Familiar
from bot.models.essence import Essence
from bot.utils.constants import GameConstants
from datetime import datetime, timedelta
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
                # 2. Deactivate current active familiar(s) and their resonance
                await session.execute(
                    update(Familiar)
                    .where(Familiar.user_id == user_id, Familiar.is_active == True)
                    .values(is_active=False, active_until=None) # End resonance on swap
                )
                
                # 3. Activate new one
                familiar.is_active = True
            
            await session.commit()
            return True, familiar
        except Exception as e:
            await session.rollback()
            return False, f"Error equipping familiar: {e}"

    @staticmethod
    async def activate_passive(session: AsyncSession, user_id: int, familiar_id: int):
        """Sets active_until to 4 hours from now. Only 2 ignites per day PER PLAYER. Must be summoned."""
        now = datetime.now()
        
        # 1. Fetch User and Familiar
        stmt_u = select(User).where(User.id == user_id)
        res_u = await session.execute(stmt_u)
        user = res_u.scalar_one_or_none()
        
        stmt_f = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
        res_f = await session.execute(stmt_f)
        familiar = res_f.scalar_one_or_none()
        
        if not user or not familiar:
            return False, "User or Familiar not found."
        
        if not familiar.is_active:
            return False, "You can only ignite resonance for your currently **summoned** familiar."

        # 2. Check Player-Level Daily Limit
        if user.last_resonance_reset.date() < now.date():
            user.daily_resonance_count = 0
            user.last_resonance_reset = now
        
        if user.daily_resonance_count >= 2:
            return False, "You have reached your limit of **2 ignites per day**. Your spirits need to rest."

        # 3. Check Familiar-Level Cooldown (Don't let same familiar ignite twice if they have slots left)
        if familiar.last_activated_at and familiar.last_activated_at.date() == now.date():
            return False, "This specific familiar has already resonated today."

        # 4. Activate for 4 hours
        async with session.begin_nested():
            familiar.last_activated_at = now
            familiar.active_until = now + timedelta(hours=4)
            user.daily_resonance_count += 1
        
        await session.commit()
        return True, familiar

    @staticmethod
    async def set_resonance_mode(session: AsyncSession, user_id: int, familiar_id: int, mode: str):
        """Switches between Echo and Pulse modes."""
        stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
        result = await session.execute(stmt)
        familiar = result.scalar_one_or_none()
        if not familiar: return False, "Familiar not found."
        
        familiar.resonance_mode = mode
        await session.commit()
        return True, familiar

    @staticmethod
    async def trigger_passive_bonus(session: AsyncSession, user_id: int, captured_type: str):
        familiar = await PassiveService.get_active_familiar(session, user_id)
        if not familiar:
            return None

        # --- Daily Active Check ---
        now = datetime.now()
        
        if not familiar.active_until or now > familiar.active_until:
            return None # Not in resonance mode
        
        # Scaling: New Lower Chances
        # Common: 8%, Uncommon: 15%, Rare: 25%, Legendary: 40%
        chance_map = {
            GameConstants.COMMON: 0.08,
            GameConstants.UNCOMMON: 0.15,
            GameConstants.RARE: 0.25,
            GameConstants.LEGENDARY: 0.40
        }
        
        chance = chance_map.get(familiar.rarity, 0.08)
        
        # Arcane familiars (+10% flat bonus)
        if familiar.essence_type == GameConstants.ARCANE:
            chance += 0.10

        if random.random() > chance:
            return None

        # Determine which essence to give
        give_type = captured_type
        if familiar.resonance_mode == "pulse":
            # Pulse Mode: Give a random DIFFERENT element
            choices = [e for e in GameConstants.ESSENCES if e != captured_type]
            give_type = random.choice(choices)
        
        # 1. Base Element check (only match in Echo mode)
        # 2. Arcane check (always works)
        can_trigger = (familiar.essence_type == captured_type) or (familiar.essence_type == GameConstants.ARCANE) or (familiar.resonance_mode == "pulse")

        if not can_trigger:
            return None

        # Grant the essence!
        stmt = select(Essence).where(Essence.user_id == user_id, Essence.type == give_type)
        res = await session.execute(stmt)
        ess = res.scalar_one_or_none()
        if not ess:
            ess = Essence(user_id=user_id, type=give_type, count=1)
            session.add(ess)
        else:
            ess.count += 1
        
        emoji = "✨" if familiar.essence_type == GameConstants.ARCANE else "🌀"
        if familiar.resonance_mode == "pulse":
            effect_msg = f"{emoji} **{familiar.name}**'s pulse transmuted the energy into {give_type} essence!"
        else:
            effect_msg = f"{emoji} **{familiar.name}**'s resonance duplicated the {captured_type} essence!"
        
        await session.commit()
        return effect_msg
