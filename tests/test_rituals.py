import pytest
from bot.services.ritual_service import RitualService
from bot.models.familiar import Spirit, Familiar
from bot.models.essence import Essence
from bot.domain.enums import EssenceType, SpiritType, Rarity
from bot.domain.constants import GameRules

@pytest.mark.asyncio
async def test_ritual_success(db_session, mock_user):
    # 1. Setup Spirit and Essence
    spirit = Spirit(user_id=mock_user.id, type=SpiritType.FELINE, rarity=Rarity.COMMON)
    essence = Essence(user_id=mock_user.id, type=EssenceType.FIRE, count=20)
    db_session.add_all([spirit, essence])
    await db_session.flush()

    # 2. Perform Ritual
    success, result = await RitualService.create_familiar(db_session, mock_user.id, spirit.id, EssenceType.FIRE)

    # 3. Assertions
    assert success is True
    assert isinstance(result, Familiar)
    assert result.rarity == Rarity.COMMON
    assert result.spirit_type == SpiritType.FELINE
    assert result.essence_type == EssenceType.FIRE
    
    # Check essence deduction (Common cost is 10)
    assert essence.count == 10

@pytest.mark.asyncio
async def test_ritual_insufficient_essence(db_session, mock_user):
    spirit = Spirit(user_id=mock_user.id, type=SpiritType.CANINE, rarity=Rarity.RARE)
    essence = Essence(user_id=mock_user.id, type=EssenceType.WATER, count=5) # Rare needs 40
    db_session.add_all([spirit, essence])
    await db_session.flush()

    success, result = await RitualService.create_familiar(db_session, mock_user.id, spirit.id, EssenceType.WATER)

    assert success is False
    assert "Insufficient" in result

@pytest.mark.asyncio
async def test_ritual_restless_requirement(db_session, mock_user):
    # Restless spirit requires matching essence + Arcane bonus
    spirit = Spirit(user_id=mock_user.id, type=SpiritType.RESTLESS, rarity=Rarity.COMMON)
    fire_essence = Essence(user_id=mock_user.id, type=EssenceType.FIRE, count=50)
    # Missing Arcane essence
    db_session.add_all([spirit, fire_essence])
    await db_session.flush()

    success, result = await RitualService.create_familiar(db_session, mock_user.id, spirit.id, EssenceType.FIRE)

    assert success is False
    assert "extra Arcane energy" in result
