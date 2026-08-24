from models.seat import Seats
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.event import Event, EventStatus
from models.user import UserRole
from utils.exceptions import EventOwnershipError

def seat_generation(rows:int, seat_per_row:int, new_event_id:int):
        l = []
        for i in range(1, rows+1):
            for j in range(1, seat_per_row+1):
                l.append(Seats(event_id=new_event_id, seat_number=f"{chr(i+64)}{j}"))  #seat db object

        return l


async def get_event_seats(   #event exit--->fetch all rows where event_id == event_id
    event_id:int,
    current_user:User,
    db:AsyncSession
):
    result = await db.execute(
        select(Event).where(Event.id == event_id)      
    )

    event = result.scalars().first()

    if event is None:
        return None

    if current_user.role == UserRole.CUSTOMER:
        if event.status != EventStatus.PUBLISHED:  #if event is not publish
            return None

    if event.status != EventStatus.PUBLISHED:
        if current_user.id != event.organiser_id or current_user.role != UserRole.ORGANISER:
            raise EventOwnershipError()
        
    result = await db.execute(
        select(Seats).where(Seats.event_id == event_id)
    )

    seats = result.scalars().all() 
    return seats

    
    


