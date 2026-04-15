import pytest
from bot.services.passive_service import PassiveService
from bot.models.familiar import Familiar
from bot.domain.enums import EssenceType, SpiritType, Rarity, ResonanceMode
from bot.domain.constants import GameRules

@pytest.mark.asyncio
async def test_resonance_mode_gating(db_session, mock_user):
    # 1. Setup Lv 1 Familiar
    familiar = Familiar(
        user_id=mock_user.id, name="Kid", level=1, is_active=True,
        spirit_type=SpiritType.FELINE, essence_type=EssenceType.FIRE, rarity=Rarity.COMMON
    )
    db_session.add(familiar)
    await db_session.flush()

    # 2. Try setting PULSE (needs Lv 5)
    success, result = await PassiveService.set_resonance_mode(db_session, mock_user.id, familiar.id, ResonanceMode.PULSE)
    assert success is False
    assert "requires Level 5" in result

    # 3. Level up to 5 and try again
    familiar.level = 5
    success, result = await PassiveService.set_resonance_mode(db_session, mock_user.id, familiar.id, ResonanceMode.PULSE)
    assert success is True
    assert familiar.resonance_mode == ResonanceMode.PULSE

@pytest.mark.asyncio
async def test_echo_matching_logic(db_session, mock_user):
    # Setup Fire Familiar, Ignited
    from datetime import datetime, timedelta
    familiar = Familiar(
        user_id=mock_user.id, name="Pyre", level=1, is_active=True,
        active_until=datetime.now() + timedelta(hours=1),
        spirit_type=SpiritType.FELINE, essence_type=EssenceType.FIRE, rarity=Rarity.LEGENDARY,
        growth_bonus=1.0 # Force 100% proc chance
    )
    db_session.add(familiar)
    await db_session.flush()

    # 1. Capture Match (Fire on Fire) -> Should trigger
    msg = await PassiveService.trigger_passive_bonus(db_session, mock_user.id, "Fire")
    assert msg is not None
    assert "duplicated" in msg

    # 2. Capture Mismatch (Water on Fire) -> Should NOT trigger
    msg = await PassiveService.trigger_passive_bonus(db_session, mock_user.id, "Water")
    assert msg is None

@pytest.mark.asyncio
async def test_arcane_universal_doubling(db_session, mock_user):
    # Setup Arcane Familiar, Ignited
    from datetime import datetime, timedelta
    familiar = Familiar(
        user_id=mock_user.id, name="Mystic", level=1, is_active=True,
        active_until=datetime.now() + timedelta(hours=1),
        spirit_type=SpiritType.RESTLESS, essence_type=EssenceType.ARCANE, rarity=Rarity.LEGENDARY,
        growth_bonus=1.0 # Force 100% proc
    )
    db_session.add(familiar)
    await db_session.flush()

    # Arcane should double ANY element
    msg = await PassiveService.trigger_passive_bonus(db_session, mock_user.id, "Earth")
    assert msg is not None
    assert "duplicated" in msg
