from schemas.venue import VenueCreate, VenueUpdate
from models.user import User
from models.venue import Venue
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from utils.exceptions import VenueOwnershipError

async def create_venue(venue_data:VenueCreate, current_user:User, db:AsyncSession):
    new_venue = Venue(
        name = venue_data.name,
        address = venue_data.address,
        city = venue_data.city,
        capacity = venue_data.capacity,
        organiser_id = current_user.id
        )
    db.add(new_venue)
    await db.commit()
    await db.refresh(new_venue)
    return new_venue

async def get_venues(db:AsyncSession):
    result = await db.execute(select(Venue))
    venues = result.scalars().all()
    return venues

async def get_venue(venue_id:int, db:AsyncSession):
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalars().first()
    if venue is None:
        return None
    return venue

async def update_venue_full(venue_id:int, venue_data:VenueCreate, current_user:User, db:AsyncSession):
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalars().first()  #venue object

    if venue is None:
        return None
    
    #ownership check
    if current_user.id != venue.organiser_id:
        raise VenueOwnershipError()
    
    venue.name = venue_data.name
    venue.address = venue_data.address
    venue.city = venue_data.city
    venue.capacity = venue_data.capacity

    await db.commit()
    await db.refresh(venue)
    return venue


async def update_venue_partial(venue_id:int, venue_data:VenueUpdate, current_user:User,  db:AsyncSession):
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalars().first()  #venue object

    if venue is None:
        return None

    #ownership check
    if current_user.id != venue.organiser_id:
        raise VenueOwnershipError()

    update_data = venue_data.model_dump(exclude_unset=True) 
    for field, value in update_data.items():
        setattr(venue, field, value)

    await db.commit()
    await db.refresh(venue)
    return venue


async def delete_venue(venue_id:int, current_user:User, db:AsyncSession):
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalars().first()

    if venue is None:
        return None
    
    #ownership check
    if current_user.id != venue.organiser_id:
        raise VenueOwnershipError()

    await db.delete(venue)
    await db.commit()
    return True
    
    
    




