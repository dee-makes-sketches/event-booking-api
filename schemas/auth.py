from pydantic import BaseModel, EmailStr, ConfigDict
from models.user import UserRole


class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str
    role:UserRole = UserRole.CUSTOMER

class MessageResponse(BaseModel):
    message:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

class UserPrivate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    username:str
    email:EmailStr
    role:UserRole



