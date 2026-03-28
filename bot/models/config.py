from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Boolean, String, DateTime
from typing import Optional
from datetime import datetime
from bot.models.base import Base

class ChannelConfig(Base):
    __tablename__ = "channel_configs"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    active_lure_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # spirit, essence, pure
    active_lure_subtype: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # Fire, etc.
    lure_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<ChannelConfig(id={self.channel_id}, active={self.is_active})>"
