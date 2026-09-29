from models.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum, func, UniqueConstraint, Index, text

from datetime import datetime
import enum

class BookingStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (Index(
        "uq_active_event_seat",
        "event_id",
        "seat_id",
        unique=True,
        postgresql_where = text("status = 'CONFIRMED'")
    ),) #Only enforce uniqueness for rows matching this condition.

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey("users.id"), nullable=False)
    event_id:Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), nullable=False)
    seat_id:Mapped[int] = mapped_column(Integer, ForeignKey("seats.id"), nullable=False)
    status:Mapped[BookingStatus] = mapped_column(Enum(BookingStatus, name="booking_status"), default=BookingStatus.CONFIRMED, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
