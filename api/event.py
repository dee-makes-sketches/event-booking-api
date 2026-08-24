from fastapi import APIRouter, HTTPException, Depends, status

from schemas.event import EventCreate, EventResponse, EventUpdateFull, EventUpdatePartial
from schemas.seat import SeatResponse
from utils.dependencies import get_db, require_role, require_organiser_or_customer
from typing import Annotated

from utils.exceptions import VenueOwnershipError, EventTimeConflictError, EventOwnershipError, SeatCapacityExceededError, EventHasActiveBookingsError
from models.user import User, UserRole

from sqlalchemy.ext.asyncio import AsyncSession
from services import event
from services import seat

router = APIRouter(prefix="/events", tags=["Events"])

db_session = Annotated[AsyncSession, Depends(get_db)]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EventResponse)
async def create_event(
    event_data:EventCreate,
    current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))],
    db:db_session
    ):
    try:
        result = await event.create_event(event_data, current_user, db)
    except VenueOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create event"
        )
    except EventTimeConflictError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event with that timing already exists"
        )
    except SeatCapacityExceededError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seat count exceeds Venue capacity"
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found"
        )

    return result

@router.get("", response_model=list[EventResponse])
async def get_events(current_user:Annotated[User, Depends(require_organiser_or_customer)], db:db_session):
    result = await event.get_events(db)
    return result


#get all event belongs to organiser regardless of its status
@router.get("/organiser", response_model=list[EventResponse])
async def get_organiser_events(
    current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))],
    db:db_session
    ):
    result = await event.get_organiser_events(current_user, db)
    return result



@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id:int, current_user:Annotated[User, Depends(require_organiser_or_customer)], db:db_session):
    result = await event.get_event(event_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return result




@router.put("/{event_id}", response_model=EventResponse)
async def update_event_full(
    event_id:int,
    event_data:EventUpdateFull,
    current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))],
    db:db_session
    ):

    try:
        result = await event.update_event_full(event_id, event_data, current_user, db)

    except EventOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            details="Not authorized to update this event"
        )

    except EventTimeConflictError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event with same time-interval already exists please try again"
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return result

@router.patch("/{event_id}", response_model=EventResponse)
async def update_event_partial(
    event_id:int,
    event_data:EventUpdatePartial,
    current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))],
    db:db_session
):
    try:
        result = await event.update_event_partial(event_id, event_data, current_user, db)
    
    except EventOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this event"
        )

    except EventTimeConflictError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event's time-interval already exists please try again"
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    return result
    
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id:int, 
    current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))],
    db:db_session
):
    try:
        result = await event.delete_event(event_id, current_user, db)
    except EventOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this event"
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )


#customer can check seat availablity
@router.get("/{event_id}/seats", response_model=list[SeatResponse])  #list of dic
async def get_event_seats(
    event_id:int,
    current_user:Annotated[User, Depends(require_organiser_or_customer)],
    db:db_session
):
    try:
        result = await seat.get_event_seats(event_id, current_user, db)

    except EventOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these seats"
        )

    except EventHasActiveBookingsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete event with existing bookings. Cancel the event instead."
        )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    return result

    
