from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.core.database import Base


if TYPE_CHECKING:
    from models.users import User


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    users: Mapped[list["User"]] = relationship("User",secondary="user_tags", back_populates="tags", cascade="all, delete-orphan", init=False)