from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.database import get_db
from schemas.auth import UserCreate, MessageResponse, UserLogin, Token
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth import register_user, login_user


router = APIRouter(prefix="/auth", tags=["Authentication"])

#dependency injection
db_session = Annotated[AsyncSession, Depends(get_db)]

#user resgistration
@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data:UserCreate, db:db_session):
    result = await register_user(user_data, db) #calls service function
    
    if result == "USER_EXISTS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User name already exists."
        )
    if result == "EMAIL_EXISTS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists."
        )
    return MessageResponse(
        message="Registration successful, Please login!"
    )

#login user and return jwt token
@router.post("/login", response_model=Token)
async def login(form_data :Annotated[OAuth2PasswordRequestForm, Depends()], db:db_session):
  
    result = await login_user(form_data, db)  #result can either be None or jwt string
    
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})

    return Token(access_token=result, token_type="bearer")

