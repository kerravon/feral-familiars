from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String, DateTime, func
from datetime import datetime
from typing import Optional
from bot.models.base import Base

class Spirit(Base):
    __tablename__ = "spirits"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))  # Feline, Canine, Winged, Goblin
    rarity: Mapped[str] = mapped_column(String(20))  # common, uncommon, rare, legendary
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<Spirit(id={self.id}, type={self.type}, rarity={self.rarity})>"

class Familiar(Base):
    __tablename__ = "familiars"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    spirit_type: Mapped[str] = mapped_column(String(20))
    essence_type: Mapped[str] = mapped_column(String(20))
    rarity: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=False)
    
    # Passive Limitation Fields
    active_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    daily_trigger_count: Mapped[int] = mapped_column(default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<Familiar(id={self.id}, name={self.name}, spirit={self.spirit_type}, essence={self.essence_type})>"
