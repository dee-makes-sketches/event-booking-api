from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from models.user import User 
from datetime import timedelta, datetime, UTC
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from typing import Annotated

#schemas
from schemas.auth import UserCreate, UserLogin

from utils.security import hash_password, verify_password, create_access_token

async def register_user(user_data:UserCreate, db:AsyncSession):
    #check username
    result = await db.execute(select(User).where(func.lower(User.username) == user_data.username.lower()))
    existing_user = result.scalars().first()

    if existing_user:
        return "USER_EXISTS"
    
    #check email
    result = await db.execute(select(User).where(func.lower(User.email) == user_data.email.lower()))
    existing_email = result.scalars().first()

    if existing_email:
        return "EMAIL_EXISTS"

    #create user and commit
    new_user = User(
        username = user_data.username,
        email = user_data.email,
        hashed_password = hash_password(user_data.password),
        role = user_data.role
    )
    db.add(new_user)
    await db.commit()
    #await db.refresh(new_user)

#login and returns token_str
async def login_user(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db:AsyncSession):
    #check email
    result = await db.execute(
        select(User)
        .where(func.lower(User.email) == form_data.username.lower())
    )
    user = result.scalars().first()
    
    if not user:
        return None
    if not verify_password(form_data.password, user.hashed_password):
        return None

    #generate jwt
    access_token_expire = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": str(user.id)}, expire_delta=access_token_expire)

    return access_token



    




