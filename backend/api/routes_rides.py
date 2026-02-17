from fastapi import APIRouter, HTTPException, Query, Header
from lib.models import RideCreateRequest, RideResponse, RideListResponse
from lib.ride_service import create_ride, search_rides, get_ride_by_id
from lib.auth_service import require_user_id

router = APIRouter()

@router.post("/", response_model=RideResponse)
def post_ride(payload: RideCreateRequest, authorization: str | None = Header(default=None)):
    try:
        user_id = require_user_id(authorization)
        payload.driver_id = user_id  # override, prevents spoofing
        return create_ride(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search", response_model=RideListResponse)
def search(from_q: str = Query(..., min_length=1), to_q: str = Query(..., min_length=1)):
    try:
        rides = search_rides(from_q, to_q)
        return RideListResponse(rides=rides)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ride_id}", response_model=RideResponse)
def ride_detail(ride_id: int):
    try:
        return get_ride_by_id(ride_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
