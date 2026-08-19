from pydantic import BaseModel, ConfigDict, Field
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

