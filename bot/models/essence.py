from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String, Integer
from bot.models.base import Base

class Essence(Base):
    __tablename__ = "essences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))  # Earth, Wind, Fire, Arcane
    count: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Essence(user_id={self.user_id}, type={self.type}, count={self.count})>"
