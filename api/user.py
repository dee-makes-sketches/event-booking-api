from fastapi import APIRouter
from utils.dependencies import CurrentUser
from schemas.auth import UserPrivate

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserPrivate)
async def get_current_user(current_user:CurrentUser):
    return current_user
