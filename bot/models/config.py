from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Boolean, String, DateTime, Enum
from typing import Optional
from datetime import datetime
from bot.models.base import Base
from bot.domain.enums import LureType, EssenceType

class ChannelConfig(Base):
    __tablename__ = "channel_configs"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    activity_score: Mapped[int] = mapped_column(default=0)
    pity_count: Mapped[int] = mapped_column(default=0)
    
    active_lure_type: Mapped[Optional[LureType]] = mapped_column(
        Enum(LureType, values_callable=lambda x: [e.value for e in x]), 
        nullable=True
    )
    active_lure_subtype: Mapped[Optional[EssenceType]] = mapped_column(
        Enum(EssenceType, values_callable=lambda x: [e.value for e in x]), 
        nullable=True
    )
    lure_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ChannelConfig(id={self.channel_id}, active={self.is_active})>"

class GuildConfig(Base):
    __tablename__ = "guild_configs"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pot_essence_total: Mapped[int] = mapped_column(default=0)
    pot_spirit_total: Mapped[int] = mapped_column(default=0)
    surge_threshold: Mapped[int] = mapped_column(default=1000)

    def __repr__(self) -> str:
        return f"<GuildConfig(id={self.guild_id}, essence={self.pot_essence_total})>"
