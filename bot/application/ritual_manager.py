import logging
from sqlalchemy.ext.asyncio import AsyncSession
from bot.services.ritual_service import RitualService
from bot.services.guidance_service import GuidanceService

logger = logging.getLogger("FeralFamiliars")

class RitualManager:
    @staticmethod
    async def perform_ritual(session: AsyncSession, user_id: int, spirit_id: int, essence_type: str):
        """
        Coordinates the ritual workflow:
        1. Call RitualService
        2. Check for Familiar milestone
        3. Commit
        """
        try:
            success, result = await RitualService.create_familiar(session, user_id, spirit_id, essence_type)
            
            if not success:
                return False, result, None

            familiar = result # Service returns familiar object
            
            # 2. Check Guidance Milestones
            tip_embed = await GuidanceService.check_milestone(session, user_id, "familiar")
            
            # 3. COMMIT
            await session.commit()
            
            return True, familiar, tip_embed

        except Exception as e:
            logger.error(f"Error in RitualManager: {e}", exc_info=True)
            await session.rollback()
            return False, "The ritual was interrupted by a void collapse. Try again.", None
