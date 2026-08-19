from fastapi import APIRouter, Depends, HTTPException, status
from schemas.venue import VenueCreate, VenueResponse, VenueUpdate
from typing import Annotated
from models.user import User, UserRole

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

from services import venue
from utils.exceptions import VenueOwnershipError

from utils.dependencies import require_role

router = APIRouter(prefix="/venues", tags=["Venues"])

db_session = Annotated[AsyncSession, Depends(get_db)]

#organiser can create venue
@router.post("",  status_code = status.HTTP_201_CREATED, response_model=VenueResponse)
async def create_venue(
    venue_data:VenueCreate, 
    current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))],
    db:db_session
    ):
    result = await venue.create_venue(venue_data, current_user, db)
    return result


#organise/customers views venues
@router.get("", response_model=list[VenueResponse])
async def get_venues(db:db_session):
    return await venue.get_venues(db)


@router.get("/{venue_id}", response_model=VenueResponse)
async def get_venue(venue_id:int, db:db_session):
    result = await venue.get_venue(venue_id, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    
    return result


#update complete venue details(organiser only )
@router.put("/{venue_id}", response_model=VenueResponse)
async def update_venue_full(venue_id:int, venue_data:VenueUpdate, current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))], db:db_session):
    try:
        result = await venue.update_venue_full(venue_id, venue_data, current_user, db)
    except VenueOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this venue")

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="venue not found"
        )
    return result

@router.patch("/{venue_id}", response_model=VenueResponse)
async def update_venue_partial(venue_id:int, venue_data:VenueUpdate, current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))], db:db_session):
    try:
        result = await venue.update_venue_partial(venue_id, venue_data, current_user, db)
    except VenueOwnershipError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this venue")

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="venue not found"
        )
    return result

#delete venue
@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(
    venue_id:int, 
    current_user:Annotated[User, Depends(require_role(UserRole.ORGANISER))],
    db:db_session
    ):
    try:
        result = await venue.delete_venue(venue_id, current_user, db)
    except VenueOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this venue"
        )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="venue not found"
        )








    
    
    

