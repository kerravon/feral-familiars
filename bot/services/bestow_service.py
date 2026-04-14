import math
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.base import User
from bot.models.essence import Essence
from bot.models.familiar import Spirit
from bot.services.inventory_service import InventoryService
from bot.services.guild_service import GuildService
from bot.domain.enums import EssenceType, Rarity
from bot.domain.constants import GameRules
from bot.utils.config import Config

class BestowService:
    @staticmethod
    async def _check_and_reset_limits(session: AsyncSession, user: User):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if user.last_gift_reset.date() != now.date():
            user.daily_spirits_gifted = 0
            user.daily_essences_gifted = 0
            user.last_gift_reset = now
            # No commit here

    @staticmethod
    async def bestow_essence(
        session: AsyncSession, 
        sender_id: int, 
        receiver_id: int, 
        essence_type: EssenceType, 
        amount: int,
        tax_payment_type: EssenceType,
        bot = None,
        guild_id: int = 0,
        channel_id: int = 0
    ):
        if amount <= 0: return False, "Amount must be positive."
        
        sender = await InventoryService.get_or_create_user(session, sender_id)
        receiver = await InventoryService.get_or_create_user(session, receiver_id)
        await BestowService._check_and_reset_limits(session, sender)

        # 1. Check Limits
        if sender.daily_essences_gifted + amount > 50:
            return False, f"Daily limit exceeded. You can only give {50 - sender.daily_essences_gifted} more essences today."

        # 2. Check Sender Inventory for items
        stmt = select(Essence).where(Essence.user_id == sender_id, Essence.type == essence_type)
        res = await session.execute(stmt)
        s_ess = res.scalar_one_or_none()
        if not s_ess or s_ess.count < amount:
            return False, f"Insufficient {essence_type.value} essences."

        # 3. Calculate Tax (3% for sender, goes to Pot)
        tax_amount = math.ceil(amount * GameRules.SOCIAL_TAX_PERCENT)
        
        # Check Sender Inventory for tax
        stmt = select(Essence).where(Essence.user_id == sender_id, Essence.type == tax_payment_type)
        res = await session.execute(stmt)
        s_tax_ess = res.scalar_one_or_none()
        
        # Total needed if tax type is the same as gift type
        total_needed = amount + tax_amount if tax_payment_type == essence_type else tax_amount
        
        if not s_tax_ess or s_tax_ess.count < total_needed:
            return False, f"You lack enough {tax_payment_type.value} for the ritual fee ({tax_amount})."

        # 4. Execute Bestow
        s_ess.count -= amount
        if tax_payment_type == essence_type:
            s_ess.count -= tax_amount
        else:
            s_tax_ess.count -= tax_amount
        
        # Add tax to the Well of Souls
        if bot and guild_id and channel_id:
            await GuildService.add_to_pot(session, guild_id, bot, channel_id, essence_amount=tax_amount)
        
        # Add to receiver
        await InventoryService.add_essence(session, receiver_id, essence_type, amount)
            
        sender.daily_essences_gifted += amount
        return True, f"You bestowed {amount} {essence_type.value} essences to <@{receiver_id}>. You paid {tax_amount} {tax_payment_type.value} to the **Well of Souls**."

    @staticmethod
    async def bestow_spirit(
        session: AsyncSession, 
        sender_id: int, 
        receiver_id: int, 
        spirit_id: int,
        tax_payment_type: EssenceType,
        bot = None,
        guild_id: int = 0,
        channel_id: int = 0
    ):
        sender = await InventoryService.get_or_create_user(session, sender_id)
        receiver = await InventoryService.get_or_create_user(session, receiver_id)
        await BestowService._check_and_reset_limits(session, sender)

        # 1. Check Limits
        if sender.daily_spirits_gifted >= 1:
            return False, "You have already gifted a spirit today."

        # Check receiver spirit limit
        stmt = select(Spirit).where(Spirit.user_id == receiver_id)
        res = await session.execute(stmt)
        r_spirits = res.scalars().all()
        if len(r_spirits) >= Config.MAX_SPIRITS:
            return False, f"Receiver's spirit inventory is full (max {Config.MAX_SPIRITS})."

        # 2. Check Spirit
        stmt = select(Spirit).where(Spirit.id == spirit_id, Spirit.user_id == sender_id)
        res = await session.execute(stmt)
        spirit = res.scalar_one_or_none()
        if not spirit:
            return False, "Spirit not found in your inventory."

        # 3. Calculate Tax
        tax_amount = GameRules.SPIRIT_TAX_MAP[spirit.rarity]

        # Check Sender Tax
        stmt = select(Essence).where(Essence.user_id == sender_id, Essence.type == tax_payment_type)
        res = await session.execute(stmt)
        s_tax_ess = res.scalar_one_or_none()
        if not s_tax_ess or s_tax_ess.count < tax_amount:
            return False, f"You lack {tax_amount} {tax_payment_type.value} for the ritual fee."

        # 4. Execute Bestow
        spirit.user_id = receiver_id
        s_tax_ess.count -= tax_amount
        sender.daily_spirits_gifted += 1
        
        # Add to Pot
        if bot and guild_id and channel_id:
            await GuildService.add_to_pot(session, guild_id, bot, channel_id, essence_amount=tax_amount, spirit_amount=1)
        
        return True, f"You bestowed a {spirit.rarity.value} {spirit.type.value} spirit to <@{receiver_id}>. You paid {tax_amount} {tax_payment_type.value} to the **Well of Souls**."
