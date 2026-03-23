from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, Boolean
from bot.models.base import Base

class ChannelConfig(Base):
    __tablename__ = "channel_configs"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<ChannelConfig(id={self.channel_id}, active={self.is_active})>"
