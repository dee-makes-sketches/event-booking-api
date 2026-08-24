
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from models.booking import Booking, BookingStatus
from models.event import Event, EventStatus
from models.seat import Seats, SeatStatus

from utils.exceptions import SeatNotAvailableError, SeatNotFoundError, EventNotPublishedError

async def create_booking(
    event_id:int,
    seat_id:int,
    current_user:User,
    db:AsyncSession
):
    #check if event exist or not
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalars().first()

    if event is None:
        return None
    
    if event.status != EventStatus.PUBLISHED:
        raise EventNotPublishedError()

    #check if seat exit in that event
    result = await db.execute(
        select(Seats).where(Seats.id == seat_id, Seats.event_id == event_id)
    )
    seat = result.scalars().first()

    if seat is None:
        raise SeatNotFoundError()

    #Seat must be available
    if seat.status != SeatStatus.AVAILABLE:
        raise SeatNotAvailableError()
    try:
    #Create the booking
        new_booking = Booking(
            user_id = current_user.id,
            event_id = event_id, 
            seat_id = seat_id,
            #seat_number = seat.seat_number learn orm relationships
            status = BookingStatus.CONFIRMED

        )
        #change seat.status
        seat.status = SeatStatus.BOOKED

        db.add(new_booking)

        await db.commit()
        await db.refresh(new_booking)

        return new_booking

    except Exception:
        await db.rollback()
        raise

async def get_bookings(
    current_user:User,
    db:AsyncSession
):
    #get list of all booking by current_user
    result = await db.execute(
        select(Booking).where(Booking.user_id == current_user.id)
    )
    bookings = result.scalars().all()
    if bookings is None:
        return None
    
    return bookings
    
async def get_booking(
    booking_id:int,
    current_user:User,
    db:AsyncSession
):
    
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.user_id == current_user.id)
    )
    booking = result.scalars().first()
    if booking is None:
        return None

    return booking

async def delete_booking(
    booking_id:int,
    current_user:User,
    db:AsyncSession
):
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.user_id == current_user.id)
    )
    booking = result.scalars().first()
    if booking is None:
        return None

    booking.status = BookingStatus.CANCELLED
    result = await db.execute(
        select(Seats).where(Seats.id == booking.seat_id)
    )
    seat = result.scalars().first()

    seat.status = SeatStatus.AVAILABLE

    await db.commit()
    return True
    
    
    
    