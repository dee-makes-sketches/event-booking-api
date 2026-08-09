#auth dependency injection
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from core.database import get_db
from fastapi.security import OAuth2PasswordBearer
from utils.security import verify_access_token
from models.user import User


outh2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token:Annotated[str, Depends(outh2_scheme)], db:Annotated[AsyncSession, Depends(get_db)]):
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid or expired token", 
                headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id_int = int(user_id)

    except(TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    #fetch user 
    result = await db.execute(
        select(User)
        .where(User.id == user_id_int)
    )
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user #authenticated user object

CurrentUser = Annotated[User, Depends(get_current_user)] #auth dependency
    
    







