import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from bot.models.trade import Trade, TradeOffer
from bot.models.essence import Essence
from bot.models.familiar import Spirit
from bot.domain.enums import EssenceType, Rarity
from bot.domain.constants import GameRules
from bot.utils.config import Config
from bot.services.inventory_service import InventoryService
from bot.services.guild_service import GuildService

class TransmuteService:
    @staticmethod
    async def create_trade(session: AsyncSession, initiator_id: int, receiver_id: int):
        trade = Trade(initiator_id=initiator_id, receiver_id=receiver_id)
        session.add(trade)
        return trade

    @staticmethod
    async def add_offer(session: AsyncSession, trade_id: int, user_id: int, type: str, subtype: str, amount: int = 1, rarity: Rarity = None, spirit_id: int = None):
        # 1. Check if user already has an offer for this essence/spirit type to update it
        if type == "essence":
            stmt = select(TradeOffer).where(TradeOffer.trade_id == trade_id, TradeOffer.user_id == user_id, TradeOffer.type == "essence", TradeOffer.subtype == subtype)
            res = await session.execute(stmt)
            offer = res.scalar_one_or_none()
            if offer:
                offer.amount = amount
                if offer.amount <= 0:
                    await session.delete(offer)
            else:
                if amount > 0:
                    offer = TradeOffer(trade_id=trade_id, user_id=user_id, type="essence", subtype=subtype, amount=amount)
                    session.add(offer)
        else: # spirit
            # check if spirit is already in trade
            stmt = select(TradeOffer).where(TradeOffer.trade_id == trade_id, TradeOffer.user_id == user_id, TradeOffer.spirit_id == spirit_id)
            res = await session.execute(stmt)
            offer = res.scalar_one_or_none()
            if not offer and amount > 0:
                offer = TradeOffer(trade_id=trade_id, user_id=user_id, type="spirit", subtype=subtype, rarity=rarity.value, amount=1, spirit_id=spirit_id)
                session.add(offer)
            elif offer and amount <= 0:
                await session.delete(offer)
        
        # Reset acceptances when offer changes
        stmt = update(Trade).where(Trade.id == trade_id).values(initiator_accepted=False, receiver_accepted=False)
        await session.execute(stmt)

    @staticmethod
    async def calculate_tax(session: AsyncSession, trade_id: int, user_id: int):
        # Calculate tax for items THIS user is RECEIVING
        stmt = select(Trade).where(Trade.id == trade_id)
        res = await session.execute(stmt)
        trade = res.scalar_one()
        
        other_id = trade.receiver_id if user_id == trade.initiator_id else trade.initiator_id
        
        # Get items from the OTHER person
        stmt = select(TradeOffer).where(TradeOffer.trade_id == trade_id, TradeOffer.user_id == other_id)
        res = await session.execute(stmt)
        offers = res.scalars().all()
        
        total_tax = 0
        for off in offers:
            if off.type == "essence":
                total_tax += math.ceil(off.amount * GameRules.SOCIAL_TAX_PERCENT)
            else:
                # Convert string rarity back to Enum for lookup
                r_enum = Rarity(off.rarity)
                total_tax += GameRules.SPIRIT_TAX_MAP[r_enum]
        
        return total_tax

    @staticmethod
    async def execute_trade(session: AsyncSession, trade_id: int, tax_types: dict, bot = None, guild_id: int = 0, channel_id: int = 0):
        # 1. Get Trade and Offers
        stmt = select(Trade).where(Trade.id == trade_id)
        res = await session.execute(stmt)
        trade = res.scalar_one()
        
        stmt = select(TradeOffer).where(TradeOffer.trade_id == trade_id)
        res = await session.execute(stmt)
        offers = res.scalars().all()

        # 2. Check Spirit Limits for both parties
        for uid in [trade.initiator_id, trade.receiver_id]:
            other_id = trade.receiver_id if uid == trade.initiator_id else trade.initiator_id
            # Spirits RECEIVING from the other person
            receiving_spirits_count = sum(1 for off in offers if off.user_id == other_id and off.type == "spirit")
            if receiving_spirits_count > 0:
                stmt = select(Spirit).where(Spirit.user_id == uid)
                res = await session.execute(stmt)
                current_spirits = res.scalars().all()
                giving_spirits_count = sum(1 for off in offers if off.user_id == uid and off.type == "spirit")
                
                if len(current_spirits) - giving_spirits_count + receiving_spirits_count > Config.MAX_SPIRITS:
                    return False, f"<@{uid}>'s spirit inventory would exceed the limit ({Config.MAX_SPIRITS})."

        # 3. Check and Deduct Taxes for both
        for uid in [trade.initiator_id, trade.receiver_id]:
            tax_amount = await TransmuteService.calculate_tax(session, trade_id, uid)
            if tax_amount > 0:
                tax_type_str = tax_types[uid]
                tax_type_enum = EssenceType(tax_type_str)
                
                stmt = select(Essence).where(Essence.user_id == uid, Essence.type == tax_type_enum)
                res = await session.execute(stmt)
                ess = res.scalar_one_or_none()
                if not ess or ess.count < tax_amount:
                    return False, f"<@{uid}> does not have enough {tax_type_str} for their ritual fee ({tax_amount})."
                ess.count -= tax_amount
                
                # Add to Pot
                if bot and guild_id and channel_id:
                    received_spirits_count = sum(1 for off in offers if off.user_id != uid and off.type == "spirit")
                    await GuildService.add_to_pot(session, guild_id, bot, channel_id, essence_amount=tax_amount, spirit_amount=received_spirits_count)

        # 4. Swap Items
        for off in offers:
            receiver_id = trade.receiver_id if off.user_id == trade.initiator_id else trade.initiator_id
            if off.type == "essence":
                # Deduct from sender
                e_enum = EssenceType(off.subtype)
                stmt = select(Essence).where(Essence.user_id == off.user_id, Essence.type == e_enum)
                res = await session.execute(stmt)
                s_ess = res.scalar_one()
                if s_ess.count < off.amount: return False, f"<@{off.user_id}> no longer has enough essences."
                s_ess.count -= off.amount
                # Add to receiver
                await InventoryService.add_essence(session, receiver_id, e_enum, off.amount)
            else:
                stmt = select(Spirit).where(Spirit.id == off.spirit_id, Spirit.user_id == off.user_id)
                res = await session.execute(stmt)
                spirit = res.scalar_one_or_none()
                if not spirit: return False, f"<@{off.user_id}> no longer has that spirit."
                spirit.user_id = receiver_id
        
        trade.status = "ACCEPTED"
        return True, "Ritual of Transmutation complete! The items have been swapped, and taxes paid to the **Well of Souls**."
