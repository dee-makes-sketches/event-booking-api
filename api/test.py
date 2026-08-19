from fastapi import Depends, APIRouter
from typing import Annotated

from models.user import User, UserRole
from utils.dependencies import require_role

router = APIRouter(prefix="/test", tags=["test-router"])




@router.get("/customer")
async def test_customer(
    current_user: Annotated[User, Depends(require_role(UserRole.CUSTOMER))]
):
    return {"message": "Customer access granted"}


@router.get("/organiser")
async def test_organiser(
    current_user: Annotated[User, Depends(require_role(UserRole.ORGANISER))]
):
    return {"message": "organiser access granted"}