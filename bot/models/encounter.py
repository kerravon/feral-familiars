from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, DateTime, func, Boolean, ForeignKey, Enum
from datetime import datetime
from typing import Optional
from bot.models.base import Base
from bot.domain.enums import EncounterType, Rarity

class Encounter(Base):
    __tablename__ = "encounters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, index=True)
    guild_id: Mapped[int] = mapped_column(BigInteger)
    type: Mapped[EncounterType] = mapped_column(
        Enum(EncounterType, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    subtype: Mapped[str] = mapped_column(String(20))  # Earth/Fire or Feline/Canine
    rarity: Mapped[Optional[Rarity]] = mapped_column(
        Enum(Rarity, values_callable=lambda x: [e.value for e in x]), 
        nullable=True
    )
    message_id: Mapped[int] = mapped_column(BigInteger)
    is_active: Mapped[bool] = mapped_column(default=True)
    spawned_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    captured_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    blacklisted_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)


    def __repr__(self) -> str:
        return f"<Encounter(id={self.id}, type={self.type}, subtype={self.subtype}, active={self.is_active})>"

class EncounterParticipant(Base):
    __tablename__ = "encounter_participants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    encounter_id: Mapped[int] = mapped_column(ForeignKey("encounters.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<EncounterParticipant(encounter_id={self.encounter_id}, user_id={self.user_id})>"
