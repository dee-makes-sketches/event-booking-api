from models.base import Base
from sqlalchemy import Integer, String, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

import enum


class SeatStatus(str, enum.Enum):
    AVAILABLE = "available"
    BOOKED = "booked"


class Seats(Base):
    __tablename__ = "seats"
    __table_args__ = (UniqueConstraint("event_id", "seat_number", name="uq_event_seat"),) #combination of event + seat should be unique 

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id:Mapped[int] = mapped_column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    seat_number:Mapped[str] = mapped_column(String, nullable=False)
    status:Mapped[SeatStatus] = mapped_column(Enum(SeatStatus, name="seat_status"), default=SeatStatus.AVAILABLE, nullable=False)
