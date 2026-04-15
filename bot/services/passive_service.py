import random
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.familiar import Familiar
from bot.models.essence import Essence
from bot.models.base import User
from bot.domain.enums import EssenceType, ResonanceMode, Rarity
from bot.domain.constants import GameRules

logger = logging.getLogger("FeralFamiliars")

class PassiveService:
    @staticmethod
    async def get_active_familiar(session: AsyncSession, user_id: int) -> Familiar:
        stmt = select(Familiar).where(Familiar.user_id == user_id, Familiar.is_active == True)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def equip_familiar(session: AsyncSession, user_id: int, familiar_id: int):
        """Summons a familiar. Does NOT commit."""
        # 1. Unsummon current
        stmt = update(Familiar).where(Familiar.user_id == user_id, Familiar.is_active == True).values(is_active=False, active_until=None)
        await session.execute(stmt)
        
        # 2. Summon new
        stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
        result = await session.execute(stmt)
        familiar = result.scalar_one_or_none()
        
        if not familiar:
            return False, "Familiar not found."
            
        familiar.is_active = True
        return True, familiar

    @staticmethod
    async def activate_passive(session: AsyncSession, user_id: int, familiar_id: int):
        """Ignites resonance. Does NOT commit."""
        stmt_u = select(User).where(User.id == user_id)
        res_u = await session.execute(stmt_u)
        user = res_u.scalar_one()
        
        # Check Daily limit (Player-level)
        now = datetime.now()
        if user.last_resonance_reset.date() != now.date():
            user.daily_resonance_count = 0
            user.last_resonance_reset = now
            
        if user.daily_resonance_count >= 2:
            return False, "You have reached your daily limit of 2 resonance ignitions."

        stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
        result = await session.execute(stmt)
        familiar = result.scalar_one_or_none()
        
        if not familiar: return False, "Familiar not found."
        if not familiar.is_active: return False, "Familiar must be summoned first."
        
        # Check if already used TODAY (Familiar-level)
        if familiar.last_activated_at and familiar.last_activated_at.date() == now.date():
            if familiar.active_until and now < familiar.active_until:
                return False, f"**{familiar.name}** is already resonating!"
            return False, f"**{familiar.name}** has already resonated today."

        familiar.active_until = now + timedelta(hours=4)
        familiar.last_activated_at = now
        user.daily_resonance_count += 1
        
        return True, familiar

    @staticmethod
    async def set_resonance_mode(session: AsyncSession, user_id: int, familiar_id: int, mode: ResonanceMode):
        """Switches resonance mode. Does NOT commit."""
        stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
        result = await session.execute(stmt)
        familiar = result.scalar_one_or_none()
        if not familiar: return False, "Familiar not found."
        
        if mode == ResonanceMode.PULSE and familiar.level < GameRules.UNLOCK_PULSE_LEVEL:
            return False, f"PULSE mode requires Level {GameRules.UNLOCK_PULSE_LEVEL}."
        if mode == ResonanceMode.ATTRACT and familiar.level < GameRules.UNLOCK_ATTRACT_LEVEL:
            return False, f"ATTRACT mode requires Level {GameRules.UNLOCK_ATTRACT_LEVEL}."
        
        familiar.resonance_mode = mode
        return True, familiar

    @staticmethod
    async def set_attract_element(session: AsyncSession, user_id: int, familiar_id: int, element: EssenceType):
        """Sets attract target. Does NOT commit."""
        stmt = select(Familiar).where(Familiar.id == familiar_id, Familiar.user_id == user_id)
        result = await session.execute(stmt)
        familiar = result.scalar_one_or_none()
        if not familiar: return False, "Familiar not found."
        
        familiar.attract_element = element
        return True, familiar

    @staticmethod
    async def trigger_passive_bonus(session: AsyncSession, user_id: int, captured_type: str):
        """Processes passive trigger. Does NOT commit."""
        familiar = await PassiveService.get_active_familiar(session, user_id)
        if not familiar:
            return None

        now = datetime.now()
        if not familiar.active_until or now > familiar.active_until:
            return None 
        
        # Dynamic Chance
        chance = GameRules.BASE_PASSIVE_CHANCE.get(familiar.rarity, 0.08)
        if familiar.essence_type == EssenceType.ARCANE:
            chance += GameRules.ARCANE_PASSIVE_BONUS
        
        chance += familiar.growth_bonus

        if random.random() > chance:
            return None

        # Determine output
        give_type = captured_type
        mode = familiar.resonance_mode
        
        if mode == ResonanceMode.PULSE:
            choices = [e.value for e in EssenceType if e.value != captured_type]
            give_type = random.choice(choices)
        elif mode == ResonanceMode.ATTRACT:
            give_type = (familiar.attract_element or EssenceType.ARCANE).value
        
        # Validation logic
        can_trigger = (familiar.essence_type.value == captured_type) or \
                      (familiar.essence_type == EssenceType.ARCANE) or \
                      (mode in [ResonanceMode.PULSE, ResonanceMode.ATTRACT])

        if not can_trigger:
            return None

        # Add item
        from bot.services.inventory_service import InventoryService
        # Converting string captured_type back to Enum for Service
        target_enum = EssenceType(give_type)
        await InventoryService.add_essence(session, user_id, target_enum, 1)
        
        emoji = "✨" if familiar.essence_type == EssenceType.ARCANE else "🌀"
        if mode == ResonanceMode.PULSE:
            effect_msg = f"{emoji} **{familiar.name}**'s pulse transmuted the energy into {give_type} essence!"
        elif mode == ResonanceMode.ATTRACT:
            effect_msg = f"{emoji} **{familiar.name}**'s attraction manifested an extra {give_type} essence!"
        else:
            effect_msg = f"{emoji} **{familiar.name}**'s resonance duplicated the {captured_type} essence!"
        
        return effect_msg
