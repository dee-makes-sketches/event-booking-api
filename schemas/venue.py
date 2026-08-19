from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class VenueCreate(BaseModel):
    name:str
    address:str
    city:str
    capacity:int = Field(gt = 0)

class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    name:str 
    address:str
    city:str
    capacity:int = Field(gt = 0)
    organiser_id:int
    created_at:datetime

class VenueUpdate(BaseModel):
    name:str | None = None
    address:str | None = None
    city:str | None = None
    capacity:int | None = Field(default=None, gt=0)



