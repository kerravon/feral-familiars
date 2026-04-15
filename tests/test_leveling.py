import pytest
from bot.services.leveling_service import LevelingService
from bot.models.familiar import Familiar
from bot.domain.enums import EssenceType, SpiritType, Rarity
from bot.domain.constants import GameRules

@pytest.mark.asyncio
async def test_xp_gain_and_level_up(db_session, mock_user):
    # 1. Setup Familiar (Level 1, 0 XP)
    familiar = Familiar(
        user_id=mock_user.id, 
        name="Test Kitty", 
        spirit_type=SpiritType.FELINE, 
        essence_type=EssenceType.FIRE, 
        rarity=Rarity.COMMON
    )
    db_session.add(familiar)
    await db_session.flush()

    # 2. Add XP (Level 1 needs 100 XP to hit Level 2)
    level_ups = await LevelingService.add_xp(db_session, familiar, 150)

    # 3. Assertions
    assert familiar.level == 2
    assert familiar.xp == 50 # 150 - 100
    assert len(level_ups) == 1
    assert level_ups[0]['level'] == 2
    assert 0.005 <= level_ups[0]['roll'] <= 0.020
    assert familiar.growth_bonus > 0

@pytest.mark.asyncio
async def test_multi_level_gain(db_session, mock_user):
    familiar = Familiar(
        user_id=mock_user.id, 
        name="Speedy", 
        spirit_type=SpiritType.WINGED, 
        essence_type=EssenceType.WIND, 
        rarity=Rarity.COMMON
    )
    db_session.add(familiar)
    await db_session.flush()

    # Cumulative XP for Lv 3 is 100 (Lv1->2) + 200 (Lv2->3) = 300
    level_ups = await LevelingService.add_xp(db_session, familiar, 350)

    assert familiar.level == 3
    assert familiar.xp == 50
    assert len(level_ups) == 2

@pytest.mark.asyncio
async def test_max_level_cap(db_session, mock_user):
    familiar = Familiar(
        user_id=mock_user.id, 
        name="Elder", 
        level=10, 
        xp=0,
        spirit_type=SpiritType.GOBLIN, 
        essence_type=EssenceType.EARTH, 
        rarity=Rarity.LEGENDARY
    )
    db_session.add(familiar)
    await db_session.flush()

    # Adding XP at max level should do nothing
    level_ups = await LevelingService.add_xp(db_session, familiar, 1000)

    assert familiar.level == 10
    assert familiar.xp == 0
    assert len(level_ups) == 0
