from models.base import Base
import enum
from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Enum, CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped

from datetime import datetime

class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (CheckConstraint("end_time > start_time", name="check_event_time"),)

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    
    title:Mapped[str] = mapped_column(String(50), nullable=False)
    description:Mapped[str] = mapped_column(String(200), nullable=False)

    start_time:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time:Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status:Mapped[EventStatus] = mapped_column(Enum(EventStatus, name="event_status"), default=EventStatus.DRAFT, nullable=False)

    venue_id:Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=False)
    organiser_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())