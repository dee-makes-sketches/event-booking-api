from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from models.event import EventStatus

class EventBase(BaseModel):
    title:str 
    description:str
    start_time:datetime
    end_time:datetime


class EventCreate(EventBase):
    status:EventStatus = EventStatus.DRAFT   #default to DRAFT
    venue_id:int = Field(gt=0)

    #seat configuration
    rows: int = Field(ge=1, le=20)
    seat_per_row: int = Field(ge=1, le=10)

class EventUpdateFull(EventBase):
    status:EventStatus

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    title:str
    description:str
    start_time:datetime
    end_time:datetime
    status:EventStatus

    venue_id:int
    organiser_id:int
    created_at:datetime
    updated_at:datetime

class EventUpdatePartial(BaseModel):

    title:str | None = None
    description:str | None = None
    start_time:datetime | None = None
    end_time:datetime | None = None
    status:EventStatus | None = None

    @model_validator(mode="after")
    def validate_event_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be strictly after start_time")
        return self
