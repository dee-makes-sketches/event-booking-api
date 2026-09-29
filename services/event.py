from sqlalchemy.ext.asyncio import AsyncSession
from schemas.event import EventCreate, EventUpdateFull, EventUpdatePartial
from models.user import User
from models.event import Event, EventStatus

from sqlalchemy import select
from services.seat import seat_generation 
from models.venue import Venue
from models.booking import Booking, BookingStatus
from utils.exceptions import VenueOwnershipError, EventTimeConflictError, EventOwnershipError, SeatCapacityExceededError, EventHasActiveBookingsError

from utils.constants import validate_status_transition
from services import booking

#organiser who owns the venue should be able to create event.
async def create_event(
    event_data: EventCreate,
    current_user: User,
    db: AsyncSession
):
    result = await db.execute(
        select(Venue).where(Venue.id == event_data.venue_id)
    )
    venue = result.scalars().first()

    if venue is None:
        return None

    # Ownership check
    if venue.organiser_id != current_user.id:
        raise VenueOwnershipError()

    # Check event time conflict
    result = await db.execute(
        select(Event).where(
            Event.venue_id == event_data.venue_id,
            Event.start_time < event_data.end_time,
            Event.end_time > event_data.start_time
        )
    )

    existing_event = result.scalars().first()

    if existing_event:
        raise EventTimeConflictError()

    try:
        new_event = Event(
            title=event_data.title,
            description=event_data.description,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            status=event_data.status,
            venue_id=event_data.venue_id,
            organiser_id=current_user.id,
        )

        db.add(new_event)

        # Get new_event.id without committing
        await db.flush()

        # Venue capacity check
        if event_data.rows * event_data.seat_per_row > venue.capacity:
            raise SeatCapacityExceededError()

        # Generate seats
        seats = seat_generation(
            rows=event_data.rows,
            seat_per_row=event_data.seat_per_row,
            new_event_id=new_event.id
        )

        db.add_all(seats)

        # Commit event + all seats together
        await db.commit()
        
        await db.refresh(new_event)

        return new_event

    except Exception:
        # Undo everything if anything fails
        await db.rollback()
        raise


#get all events
async def get_events(db:AsyncSession):
    result = await db.execute(
        select(Event)
        .where(Event.status == EventStatus.PUBLISHED)
    )
    events = result.scalars().all()

    if events is None:
        return None

    return events

#get specific event by its id
async def get_event(event_id:int, db:AsyncSession):
    result = await db.execute(
        select(Event)
        .where(Event.id == event_id, Event.status == EventStatus.PUBLISHED)
    )

    event = result.scalars().first()
    if event is None:
        return None
    
    return event

#get all event belongs to organiser regardless of its status
async def get_organiser_events(
    current_user:User,
    db:AsyncSession
):
    result = await db.execute(
        select(Event)
        .where(Event.organiser_id == current_user.id)
    )

    organiser_events = result.scalars().all()
    return organiser_events


async def update_event_full(  
    event_id:int,  
    event_data:EventUpdateFull,
    current_user:User,
    db:AsyncSession
    ):

    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalars().first()

    if event is None:
        return None

    #does this evem belongs to current organiser
    if event.organiser_id != current_user.id:
        raise EventOwnershipError()

    #time interval conflict (checking if any other event exist with the conflicting time-interval)
    result = await db.execute(
        select(Event)
        .where(Event.venue_id == event.venue_id,
            Event.id != event.id,   #so it doesnt fetch itself
            Event.start_time < event_data.end_time,
            Event.end_time > event_data.start_time
        )
    )
    existing_event = result.scalars().first()
    if existing_event:
        raise EventTimeConflictError()

    #valid state transition 
    if event_data.status != event.status:
        validate_status_transition(
            event.status,
            event_data.status
        )

        #event is being cancelled
        if event_data.status == EventStatus.CANCELLED:
            await booking.cancel_event_bookings(event.id, db)



    event.title = event_data.title
    event.description = event_data.description
    event.start_time = event_data.start_time
    event.end_time = event_data.end_time
    event.status= event_data.status

    await db.commit()
    await db.refresh(event)
    return event


async def update_event_partial(
    event_id:int,
    event_data:EventUpdatePartial,
    current_user:User,
    db:AsyncSession
):
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalars().first()

    if event is None:
        return None
    
    #ownership check
    if event.organiser_id != current_user.id:
        raise EventOwnershipError()

    updated_data = event_data.model_dump(exclude_unset=True) #dict

    if "start_time" in updated_data or "end_time" in updated_data:
        new_start = updated_data.get("start_time", event.start_time)
        new_end = updated_data.get("end_time", event.end_time)

        #time conflict check
        result = await db.execute(
            select(Event)
            .where(Event.venue_id == event.venue_id,
                   Event.id != event.id,
                   Event.start_time < new_end,
                   Event.end_time > new_start
            )
        )

    existing_event = result.scalars().first()
    
    if existing_event:
        raise EventTimeConflictError()

    # valid state transition
    if "status" in updated_data:
        if updated_data["status"] != event.status:
            validate_status_transition(
                event.status,
                updated_data["status"]
            )
        #event is being cancelled
        if updated_data["status"] == EventStatus.CANCELLED:
            await booking.cancel_event_bookings(event.id,db)


    for field, value in updated_data.items():
        setattr(event, field, value)

    await db.commit()
    await db.refresh(event)
    return event


async def delete_event(
    event_id:int, 
    current_user:User,
    db:AsyncSession
):
    #check if event exit
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalars().first()

    if event is None:
        return None

    #ownership check
    if event.organiser_id != current_user.id:
        raise EventOwnershipError()

    if event.status == EventStatus.DRAFT:
        await db.delete(event)
        await db.commit()
        return True

    #await db.delete(event) dont blindly delete event 
    event.status = EventStatus.CANCELLED
   
    await db.commit()
    return True






    
        
    

    

