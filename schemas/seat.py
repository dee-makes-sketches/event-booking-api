from pydantic import BaseModel, ConfigDict
from models.seat import SeatStatus

class SeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    seat_number:str
    status:SeatStatus