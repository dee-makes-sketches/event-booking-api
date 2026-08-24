from pydantic import BaseModel, Field, ConfigDict
from models.booking import BookingStatus

class BookingCreate(BaseModel):
    event_id:int = Field(gt=0)
    seat_id:int = Field(gt=0)
    

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int 
    event_id:int
    #seat_number:str
    status:BookingStatus