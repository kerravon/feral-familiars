from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from bot.models.base import User
from bot.models.essence import Essence
from bot.models.familiar import Spirit
from bot.services.inventory_service import InventoryService
from bot.utils.constants import GameConstants
from datetime import datetime, timezone
import math

class BestowService:
    @staticmethod
    async def _check_and_reset_limits(session: AsyncSession, user: User):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        # Check if last reset was on a different day
        if user.last_gift_reset.date() < now.date():
            user.daily_spirits_gifted = 0
            user.daily_essences_gifted = 0
            user.last_gift_reset = now
            await session.commit()

    @staticmethod
    async def bestow_essence(
        session: AsyncSession, 
        sender_id: int, 
        receiver_id: int, 
        essence_type: str, 
        amount: int,
        tax_payment_type: str
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
            return False, f"Insufficient {essence_type} essences."

        # 3. Calculate Tax (2% for sender)
        tax_amount = math.ceil(amount * 0.02)
        
        # Check Sender Inventory for tax
        stmt = select(Essence).where(Essence.user_id == sender_id, Essence.type == tax_payment_type)
        res = await session.execute(stmt)
        s_tax_ess = res.scalar_one_or_none()
        
        # Total needed if tax type is the same as gift type
        total_needed = amount + tax_amount if tax_payment_type == essence_type else tax_amount
        
        if not s_tax_ess or s_tax_ess.count < (amount + tax_amount if tax_payment_type == essence_type else tax_amount):
            return False, f"You lack enough {tax_payment_type} for the ritual fee ({tax_amount})."

        # 4. Execute Bestow
        s_ess.count -= amount
        # Re-fetch or use the same object for tax if types match
        if tax_payment_type == essence_type:
            s_ess.count -= tax_amount
        else:
            s_tax_ess.count -= tax_amount
        
        # Add to receiver
        stmt = select(Essence).where(Essence.user_id == receiver_id, Essence.type == essence_type)
        res = await session.execute(stmt)
        r_ess = res.scalar_one_or_none()
        if not r_ess:
            r_ess = Essence(user_id=receiver_id, type=essence_type, count=amount)
            session.add(r_ess)
        else:
            r_ess.count += amount
            
        sender.daily_essences_gifted += amount
        await session.commit()
        return True, f"You bestowed {amount} {essence_type} essences to <@{receiver_id}>. You paid a ritual fee of {tax_amount} {tax_payment_type}."

    @staticmethod
    async def bestow_spirit(
        session: AsyncSession, 
        sender_id: int, 
        receiver_id: int, 
        spirit_id: int,
        tax_payment_type: str
    ):
        sender = await InventoryService.get_or_create_user(session, sender_id)
        receiver = await InventoryService.get_or_create_user(session, receiver_id)
        await BestowService._check_and_reset_limits(session, sender)

        # 1. Check Limits
        if sender.daily_spirits_gifted >= 1:
            return False, "You have already gifted a spirit today."

        # 2. Check Spirit
        stmt = select(Spirit).where(Spirit.id == spirit_id, Spirit.user_id == sender_id)
        res = await session.execute(stmt)
        spirit = res.scalar_one_or_none()
        if not spirit:
            return False, "Spirit not found in your inventory."

        # 3. Calculate Tax
        transmute_tax = {
            GameConstants.COMMON: 2,
            GameConstants.UNCOMMON: 5,
            GameConstants.RARE: 10,
            GameConstants.LEGENDARY: 25
        }
        tax_amount = math.ceil(transmute_tax[spirit.rarity] / 2)

        # Check Sender Tax
        stmt = select(Essence).where(Essence.user_id == sender_id, Essence.type == tax_payment_type)
        res = await session.execute(stmt)
        s_tax_ess = res.scalar_one_or_none()
        if not s_tax_ess or s_tax_ess.count < tax_amount:
            return False, f"You lack {tax_amount} {tax_payment_type} for the ritual fee."

        # 4. Execute Bestow
        spirit.user_id = receiver_id
        s_tax_ess.count -= tax_amount
        sender.daily_spirits_gifted += 1
        
        await session.commit()
        return True, f"You bestowed a {spirit.rarity} {spirit.type} spirit to <@{receiver_id}>. You paid a ritual fee of {tax_amount} {tax_payment_type}."
