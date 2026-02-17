from fastapi import APIRouter, HTTPException, Header
from lib.models import UserProfileResponse
from lib.auth_service import get_user_profile, require_user_id

router = APIRouter()

@router.get("/me", response_model=UserProfileResponse)
def profile_me(authorization: str | None = Header(default=None)):
    try:
        user_id = require_user_id(authorization)
        return get_user_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/{user_id}", response_model=UserProfileResponse)
def profile(user_id: int):
    try:
        return get_user_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
