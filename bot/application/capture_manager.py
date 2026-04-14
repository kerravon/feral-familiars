import asyncio
import logging
import discord
from sqlalchemy.ext.asyncio import AsyncSession
from bot.services.encounter_service import EncounterService
from bot.services.passive_service import PassiveService
from bot.services.leveling_service import LevelingService
from bot.services.guidance_service import GuidanceService
from bot.domain.enums import EncounterType, EssenceType
from bot.domain.constants import GameRules

logger = logging.getLogger("FeralFamiliars")

class CaptureManager:
    @staticmethod
    async def process_capture(session: AsyncSession, channel_id: int, user_id: int, keyword: str):
        """
        Coordinates the entire capture workflow: 
        1. Process the attempt (Service)
        2. Award XP (Progression)
        3. Trigger Passives (Passive)
        4. Check Milestones (Guidance)
        5. Return results for UI
        """
        # 1. Logic Layer: Process the raw capture attempt
        encounter, result_msg = await EncounterService.process_capture_attempt(session, channel_id, user_id, keyword)
        
        if not encounter:
            return None, result_msg, None, None, []

        try:
            # --- Successful Capture Workflow ---
            
            # 2. Trigger Passive Bonuses (if essence)
            passive_msg = None
            if encounter.type == EncounterType.ESSENCE:
                passive_msg = await PassiveService.trigger_passive_bonus(session, user_id, encounter.subtype)

            # 3. Award XP to summoned familiar
            level_up_events = []
            active_fam = await PassiveService.get_active_familiar(session, user_id)
            if active_fam:
                is_match = (encounter.type == EncounterType.ESSENCE and encounter.subtype == active_fam.essence_type)
                xp_amount = GameRules.XP_PER_MATCHING_CAPTURE if is_match else GameRules.XP_PER_CAPTURE
                level_up_events = await LevelingService.add_xp(session, active_fam, xp_amount)

            # 4. Check Guidance Milestones
            tip_embed = await GuidanceService.check_milestone(session, user_id, encounter.type.value)

            # 5. COMMIT THE ENTIRE TRANSACTION
            await session.commit()
            
            return encounter, result_msg, passive_msg, tip_embed, level_up_events

        except Exception as e:
            logger.error(f"Error in CaptureManager: {e}", exc_info=True)
            await session.rollback()
            return None, "A mystical surge prevented the binding. Try again.", None, None, []
