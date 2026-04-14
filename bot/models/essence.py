from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, String, Integer, Enum
from bot.models.base import Base
from bot.domain.enums import EssenceType

class Essence(Base):
    __tablename__ = "essences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    # Use the values of the Enum for the DB
    type: Mapped[EssenceType] = mapped_column(
        Enum(EssenceType, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    count: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<Essence(user_id={self.user_id}, type={self.type}, count={self.count})>"
