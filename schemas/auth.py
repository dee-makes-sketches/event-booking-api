from pydantic import BaseModel, EmailStr
from models.user import UserRole
#register
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
    id:int
    username:str
    email:EmailStr
    role:UserRole



