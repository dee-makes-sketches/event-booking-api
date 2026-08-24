from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserRole
from core.database import get_db

from services import booking
from utils.dependencies import require_role

from schemas.booking import BookingResponse
from utils.exceptions import SeatNotAvailableError, SeatNotFoundError, EventNotPublishedError


router = APIRouter(prefix="/bookings", tags=["Bookings"])


db_session = Annotated[AsyncSession, Depends(get_db)]

#create bookings
@router.post("", response_model=BookingResponse)
async def create_booking(
    event_id:int,
    seat_id:int,
    current_user:Annotated[User, Depends(require_role(UserRole.CUSTOMER))],
    db:db_session
):
    try:
        result = await booking.create_booking(event_id, seat_id, current_user, db)
    except SeatNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )
    except SeatNotAvailableError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat is already booked"
        )
    except EventNotPublishedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bookings are not available for this event"
        )    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return result

@router.get("", response_model=list[BookingResponse])
async def get_bookings(
    current_user:Annotated[User, Depends(require_role(UserRole.CUSTOMER))],
    db:db_session
):
    result = await booking.get_bookings(current_user, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookings not found"
        )
    return result

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id:int,
    current_user:Annotated[User, Depends(require_role(UserRole.CUSTOMER))],
    db:db_session    
):
    result = await booking.get_booking(booking_id, current_user, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or Access denied"
        )
    return result

@router.delete("/{booking_id}/cancel", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id:int,
    current_user:Annotated[User, Depends(require_role(UserRole.CUSTOMER))],
    db:db_session
):
    result = await booking.delete_booking(booking_id, current_user, db)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or access denied"
        )
