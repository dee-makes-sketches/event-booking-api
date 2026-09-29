#auth dependency injection
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from core.database import get_db
from fastapi.security import OAuth2PasswordBearer
from utils.security import verify_access_token
from models.user import User, UserRole


outh2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token:Annotated[str, Depends(outh2_scheme)], db:Annotated[AsyncSession, Depends(get_db)]):

    user_id = verify_access_token(token)   #extraction happend due to outh2_scheme function

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


#role dependency
def require_role(required_role:UserRole):
    async def role_checker(current_user:CurrentUser): #dependecy is called here automatically
        
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission for this action"
            )
        return current_user
    return role_checker


def require_organiser_or_customer(current_user:CurrentUser):
    if current_user.role not in [UserRole.CUSTOMER, UserRole.ORGANISER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return current_user

"""def require_customer(current_user:CurrentUser):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return current_user"""








