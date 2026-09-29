
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.user import User
from models.booking import Booking, BookingStatus
from models.event import Event, EventStatus
from models.seat import Seats, SeatStatus
from schemas.booking import BookingCreate
from utils.exceptions import SeatNotAvailableError, SeatNotFoundError, EventNotPublishedError, ForcedBookingFailure, EventOwnershipError, BookingAlreadyCancelledError

async def create_booking(
    booking_data: BookingCreate,
    current_user: User,
    db: AsyncSession
):
    result = await db.execute(
        select(Event).where(
            Event.id == booking_data.event_id
        )
    )

    event = result.scalars().first()

    if event is None:
        return None

    if event.status != EventStatus.PUBLISHED:
        raise EventNotPublishedError()

    result = await db.execute(
        select(Seats)
        .where(
            Seats.id == booking_data.seat_id,
            Seats.event_id == booking_data.event_id
        ).with_for_update()
    )

    seat = result.scalars().first()

    if seat is None:
        raise SeatNotFoundError()

    if seat.status != SeatStatus.AVAILABLE:
        raise SeatNotAvailableError()


    try:
        new_booking = Booking(
            user_id=current_user.id,
            event_id=booking_data.event_id,
            seat_id=booking_data.seat_id,
            status=BookingStatus.CONFIRMED
        )

        seat.status = SeatStatus.BOOKED

        db.add(new_booking)

        # delibrate application crash test
        #if current_user.username == "case_d_user_a":
        #   raise ForcedBookingFailure()

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
    try:

        result = await db.execute(
            select(Booking).where(Booking.id == booking_id, Booking.user_id == current_user.id)
        )
        booking = result.scalars().first()

        if booking is None:
            return None

        # transition check (cancellation twice)
        if booking.status == BookingStatus.CANCELLED:
            raise BookingAlreadyCancelledError()
        
        booking.status = BookingStatus.CANCELLED

        result = await db.execute(
            select(Seats).where(Seats.id == booking.seat_id)
        )

        seat = result.scalars().first()

        seat.status = SeatStatus.AVAILABLE

        await db.commit()
        return True
    
    except Exception:
        await db.rollback()
        raise




#helper function
async def cancel_event_bookings(
        event_id:int,
        db:AsyncSession
):
    result = await db.execute(
        update(Booking)
        .where(
            Booking.event_id == event_id,
            Booking.status == BookingStatus.CONFIRMED
        )
        .values(status=BookingStatus.CANCELLED)
    )


async def get_organiser_bookings(
    current_user:User,
    db:AsyncSession
):
    #get all the bookings associated with the event belonging to auth organiser.
    result = await db.execute(
        select(Booking)
        .join(Event, Booking.event_id == Event.id )
        .where(Event.organiser_id == current_user.id)
    )
    bookings = result.scalars().all()

    return bookings


async def get_event_bookings(
    event_id:int,
    current_user:User,
    db:AsyncSession
):
    """result = await db.execute(
        select(Booking)
        .join(Event, Booking.event_id == Event.id)
        .where(Event.organiser_id == current_user.id, Event.id == event_id)

    )

    bookings = result.scalars().all()

    return bookings"""

    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalars().first()

    if event is None:
        return None
    
    #ownership check
    if event.organiser_id != current_user.id:
        raise EventOwnershipError() 

    result = await db.execute(select(Booking).where(Booking.event_id == event_id))

    bookings = result.scalars().all()

    return bookings
        
