from models.base import Base

from datetime import datetime
from sqlalchemy import INTEGER, String, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

class Venue(Base):
    __tablename__ = "venues"
    __table_args__ = (CheckConstraint("capacity > 0", name="ck_venues_capacity_positive"), )

    id:Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    name:Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    address:Mapped[str] = mapped_column(String(200), nullable=False)
    city:Mapped[str] = mapped_column(String, nullable=False)
    capacity:Mapped[int] = mapped_column(INTEGER, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    organiser_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)



