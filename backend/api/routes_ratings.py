from fastapi import APIRouter, HTTPException, Header
from lib.models import RatingCreateRequest, RatingSummaryResponse, MessageResponse
from lib.rating_service import submit_rating, get_driver_rating_summary
from lib.auth_service import require_user_id
from lib.ride_service import get_ride_by_id

router = APIRouter()

@router.post("/", response_model=MessageResponse)
def rate_driver(payload: RatingCreateRequest, authorization: str | None = Header(default=None)):
    try:
        user_id = require_user_id(authorization)
        payload.rater_id = user_id

        ride = get_ride_by_id(int(payload.ride_id))
        payload.driver_id = int(ride["driver_id"])

        submit_rating(payload)
        return MessageResponse(message="Rating submitted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/driver/{driver_id}", response_model=RatingSummaryResponse)
def driver_rating(driver_id: int):
    try:
        return get_driver_rating_summary(driver_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
