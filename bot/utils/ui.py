import discord
from discord import ui
from bot.services.transmute_service import TransmuteService
from bot.services.inventory_service import InventoryService
from bot.db import AsyncSessionLocal
from bot.utils.constants import GameConstants
import math

class EssenceOfferModal(ui.Modal, title="Offer Essences"):
    essence_type = ui.TextInput(label="Essence Type", placeholder="Fire, Water, etc.", min_length=3, max_length=10)
    amount = ui.TextInput(label="Amount", placeholder="e.g. 10", min_length=1, max_length=3)

    def __init__(self, trade_id, view):
        super().__init__()
        self.trade_id = trade_id
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        etype = self.essence_type.value.title()
        if etype not in GameConstants.ESSENCES:
            await interaction.response.send_message(f"Invalid essence type: {etype}", ephemeral=True)
            return
        
        try:
            amt = int(self.amount.value)
            if amt < 0: raise ValueError()
        except ValueError:
            await interaction.response.send_message("Amount must be a positive number.", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            # Check if user has enough
            essences = await InventoryService.get_essences(session, interaction.user.id)
            user_ess = next((e for e in essences if e.type == etype), None)
            if not user_ess or user_ess.count < amt:
                await interaction.response.send_message(f"You don't have {amt} {etype} essences.", ephemeral=True)
                return

            await TransmuteService.add_offer(session, self.trade_id, interaction.user.id, "essence", etype, amount=amt)
        
        await self.view.update_message(interaction)

class SpiritOfferModal(ui.Modal, title="Offer a Spirit"):
    spirit_id = ui.TextInput(label="Spirit ID", placeholder="Find the ID in your /inventory", min_length=1, max_length=10)

    def __init__(self, trade_id, view):
        super().__init__()
        self.trade_id = trade_id
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            sid = int(self.spirit_id.value)
        except ValueError:
            await interaction.response.send_message("ID must be a number.", ephemeral=True)
            return

        async with AsyncSessionLocal() as session:
            # Verify spirit ownership
            spirits = await InventoryService.get_spirits(session, interaction.user.id)
            spirit = next((s for s in spirits if s.id == sid), None)
            if not spirit:
                await interaction.response.send_message("Spirit not found in your inventory.", ephemeral=True)
                return

            await TransmuteService.add_offer(session, self.trade_id, interaction.user.id, "spirit", spirit.type, rarity=spirit.rarity, spirit_id=sid)
        
        await self.view.update_message(interaction)

class TransmuteView(ui.View):
    def __init__(self, trade_id, initiator_id, receiver_id, bot=None):
        super().__init__(timeout=300) # 5 minute timeout
        self.trade_id = trade_id
        self.initiator_id = initiator_id
        self.receiver_id = receiver_id
        self.bot = bot
        self.initiator_accepted = False
        self.receiver_accepted = False
        # Default tax payment to Arcane, players can't change in MVP yet
        self.tax_types = {initiator_id: "Arcane", receiver_id: "Arcane"}

    async def update_message(self, interaction: discord.Interaction):
        from sqlalchemy import select
        from bot.models.trade import Trade, TradeOffer
        
        async with AsyncSessionLocal() as session:
            stmt = select(TradeOffer).where(TradeOffer.trade_id == self.trade_id)
            res = await session.execute(stmt)
            offers = res.scalars().all()
            
            # Re-fetch acceptance status
            stmt = select(Trade).where(Trade.id == self.trade_id)
            res = await session.execute(stmt)
            trade = res.scalar_one()
            self.initiator_accepted = trade.initiator_accepted
            self.receiver_accepted = trade.receiver_accepted

            embed = discord.Embed(title="✨ Ritual of Transmutation", color=discord.Color.purple())
            
            for uid, name in [(self.initiator_id, "Initiator"), (self.receiver_id, "Receiver")]:
                u_offers = [o for o in offers if o.user_id == uid]
                text = ""
                for o in u_offers:
                    if o.type == "essence": text += f"▫️ {o.amount}x {o.subtype}\n"
                    else: text += f"▫️ {o.rarity.title()} {o.subtype} (ID: {o.spirit_id})\n"
                
                tax = await TransmuteService.calculate_tax(session, self.trade_id, uid)
                status = "✅ READY" if (uid == self.initiator_id and self.initiator_accepted) or (uid == self.receiver_id and self.receiver_accepted) else "⌛ Offering..."
                
                embed.add_field(
                    name=f"<@{uid}>'s Offer ({status})", 
                    value=f"{text or 'Empty'}\n*Fee: {tax} essences*", 
                    inline=True
                )

            embed.set_footer(text="Both must Confirm to complete. Any change resets status.")
            
            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="Offer Essence", style=discord.ButtonStyle.secondary)
    async def offer_essence(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("You are not part of this ritual.", ephemeral=True)
            return
        await interaction.response.send_modal(EssenceOfferModal(self.trade_id, self))

    @ui.button(label="Offer Spirit", style=discord.ButtonStyle.secondary)
    async def offer_spirit(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("You are not part of this ritual.", ephemeral=True)
            return
        await interaction.response.send_modal(SpiritOfferModal(self.trade_id, self))

    @ui.button(label="Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("You are not part of this ritual.", ephemeral=True)
            return

        from sqlalchemy import update
        from bot.models.trade import Trade
        
        async with AsyncSessionLocal() as session:
            if interaction.user.id == self.initiator_id:
                self.initiator_accepted = True
                stmt = update(Trade).where(Trade.id == self.trade_id).values(initiator_accepted=True)
            else:
                self.receiver_accepted = True
                stmt = update(Trade).where(Trade.id == self.trade_id).values(receiver_accepted=True)
            
            await session.execute(stmt)
            await session.commit()

            if self.initiator_accepted and self.receiver_accepted:
                # Final Execution
                success, msg = await TransmuteService.execute_trade(
                    session, self.trade_id, self.tax_types, 
                    bot=self.bot, guild_id=interaction.guild_id, channel_id=interaction.channel_id
                )
                if success:
                    self.stop()
                    await interaction.response.edit_message(content=f"✅ **Ritual Complete!** {msg}", view=None)
                else:
                    await interaction.response.send_message(f"❌ **Ritual Failed:** {msg}", ephemeral=True)
            else:
                await self.update_message(interaction)

    @ui.button(label="Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id not in [self.initiator_id, self.receiver_id]:
            await interaction.response.send_message("You are not part of this ritual.", ephemeral=True)
            return
        self.stop()
        await interaction.response.edit_message(content="❌ **Ritual Aborted.**", embed=None, view=None)

class FamiliarModeSelect(ui.Select):
    def __init__(self, familiar):
        options = [
            discord.SelectOption(label="ECHO", value="echo", description="Double captured element (Lv. 1)", emoji="🔁")
        ]
        if familiar.level >= 5:
            options.append(discord.SelectOption(label="PULSE", value="pulse", description="Random different element (Lv. 5)", emoji="🔄"))
        if familiar.level >= 8:
            options.append(discord.SelectOption(label="ATTRACT", value="attract", description="Targeted element (Lv. 8)", emoji="🎯"))
            
        super().__init__(placeholder="Choose Resonance Mode...", min_values=1, max_values=1, options=options)
        self.familiar_id = familiar.id

    async def callback(self, interaction: discord.Interaction):
        from bot.services.passive_service import PassiveService
        async with AsyncSessionLocal() as session:
            success, result = await PassiveService.set_resonance_mode(session, interaction.user.id, self.familiar_id, self.values[0])
            if success:
                await interaction.response.send_message(f"✅ Resonance mode set to **{self.values[0].upper()}**.", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ {result}", ephemeral=True)

class FamiliarView(ui.View):
    def __init__(self, familiar, user_id):
        super().__init__(timeout=60)
        self.familiar_id = familiar.id
        self.user_id = user_id
        self.add_item(FamiliarModeSelect(familiar))

    @ui.button(label="Ignite Resonance", style=discord.ButtonStyle.danger, emoji="🔥")
    async def ignite(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your familiar.", ephemeral=True)
            return

        from bot.services.passive_service import PassiveService
        async with AsyncSessionLocal() as session:
            success, result = await PassiveService.activate_passive(session, self.user_id, self.familiar_id)
            
            if success:
                button.disabled = True
                button.label = "Resonating..."
                await interaction.response.edit_message(view=self)
                await interaction.followup.send(f"🔥 **{result.name}'s resonance has been ignited!** Passive effects are active for the next 4 hours.")
            else:
                await interaction.response.send_message(f"❌ {result}", ephemeral=True)
