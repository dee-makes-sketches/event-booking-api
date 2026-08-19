from sqlalchemy.ext.asyncio import AsyncSession
from schemas.event import EventCreate, EventUpdateFull, EventUpdatePartial
from models.user import User
from models.event import Event, EventStatus

from sqlalchemy import select, func
from models.venue import Venue
from utils.exceptions import VenueOwnershipError, EventTimeConflictError, EventOwnershipError


#organiser who owns the venue should be able to create event
async def create_event(
    event_data:EventCreate,
    current_user:User,
    db:AsyncSession
    ):
    result = await db.execute(select(Venue).where(Venue.id == event_data.venue_id))
    venue = result.scalars().first()

    if venue is None:
        return None

    #ownership check
    if venue.organiser_id != current_user.id :
        raise VenueOwnershipError()

    #check event time conflict
    result = await db.execute(
        select(Event)
        .where(
            Event.venue_id == event_data.venue_id, #all events that has venue_id same as requested one
            Event.start_time < event_data.end_time,
            Event.end_time > event_data.start_time
        )
    )
    existing_event = result.scalars().first()
    if existing_event:
        raise EventTimeConflictError()

    new_event = Event(
        title = event_data.title,
        description = event_data.description,
        start_time = event_data.start_time,
        end_time = event_data.end_time,
        status = event_data.status,
        venue_id = event_data.venue_id,
        organiser_id=current_user.id

    )
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return new_event

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

    await db.delete(event)
    await db.commit()
    return True



    
        
    

    

