from models.base import Base
import enum

from datetime import datetime
from sqlalchemy import INTEGER, String, DateTime, func, Enum
from sqlalchemy.orm import mapped_column, Mapped

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ORGANISER = "organiser"


class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(INTEGER, primary_key=True, index=True)
    username:Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email:Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    hashed_password:Mapped[str] = mapped_column(String(100), nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    role:Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.CUSTOMER, nullable=False)
    
