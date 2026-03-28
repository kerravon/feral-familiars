from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, func
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Discord User ID
    stable_limit: Mapped[int] = mapped_column(default=5)
    daily_spirits_gifted: Mapped[int] = mapped_column(default=0)
    daily_essences_gifted: Mapped[int] = mapped_column(default=0)
    last_gift_reset: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Lure Storage (Minutes)
    stored_essence_lure_mins: Mapped[int] = mapped_column(default=0)
    stored_spirit_lure_mins: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, stable_limit={self.stable_limit})>"
