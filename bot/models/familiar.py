from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String, DateTime, func, Enum
from datetime import datetime
from typing import Optional
from bot.models.base import Base
from bot.domain.enums import SpiritType, EssenceType, Rarity, ResonanceMode

class Spirit(Base):
    __tablename__ = "spirits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    type: Mapped[SpiritType] = mapped_column(
        Enum(SpiritType, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    rarity: Mapped[Rarity] = mapped_column(
        Enum(Rarity, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<Spirit(id={self.id}, type={self.type}, rarity={self.rarity})>"

class Familiar(Base):
    __tablename__ = "familiars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    spirit_type: Mapped[SpiritType] = mapped_column(
        Enum(SpiritType, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    essence_type: Mapped[EssenceType] = mapped_column(
        Enum(EssenceType, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    rarity: Mapped[Rarity] = mapped_column(
        Enum(Rarity, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=False)
    
    # Passive Limitation Fields
    active_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    daily_trigger_count: Mapped[int] = mapped_column(default=0)
    
    # Leveling Fields
    level: Mapped[int] = mapped_column(default=1)
    xp: Mapped[int] = mapped_column(default=0)
    growth_bonus: Mapped[float] = mapped_column(default=0.0)
    
    # Resonance Customization
    resonance_mode: Mapped[ResonanceMode] = mapped_column(
        Enum(ResonanceMode, values_callable=lambda x: [e.value for e in x]), 
        default=ResonanceMode.ECHO
    )
    attract_element: Mapped[Optional[EssenceType]] = mapped_column(
        Enum(EssenceType, values_callable=lambda x: [e.value for e in x]), 
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<Familiar(id={self.id}, name={self.name}, spirit={self.spirit_type}, essence={self.essence_type})>"
