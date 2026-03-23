from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, String, DateTime, func, ForeignKey, Boolean
from datetime import datetime
from bot.models.base import Base

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    initiator_id: Mapped[int] = mapped_column(BigInteger, index=True)
    receiver_id: Mapped[int] = mapped_column(BigInteger, index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING, ACCEPTED, CANCELLED
    initiator_accepted: Mapped[bool] = mapped_column(default=False)
    receiver_accepted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class TradeOffer(Base):
    __tablename__ = "trade_offers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trade_id: Mapped[int] = mapped_column(ForeignKey("trades.id"), index=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    type: Mapped[str] = mapped_column(String(20))  # essence, spirit
    subtype: Mapped[str] = mapped_column(String(20))  # Earth/Feline/etc.
    rarity: Mapped[str] = mapped_column(String(20), nullable=True)
    amount: Mapped[int] = mapped_column(default=1)
    spirit_id: Mapped[int] = mapped_column(BigInteger, nullable=True) # ID of specific spirit being traded
