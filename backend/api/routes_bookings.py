from fastapi import APIRouter, HTTPException, Header
from lib.models import BookingCreateRequest, BookingResponse, BookingListResponse, MessageResponse
from lib.booking_service import create_booking, cancel_booking, get_user_bookings
from lib.auth_service import require_user_id

router = APIRouter()

@router.post("/", response_model=BookingResponse)
def book_ride(payload: BookingCreateRequest, authorization: str | None = Header(default=None)):
    try:
        user_id = require_user_id(authorization)
        payload.rider_id = user_id
        return create_booking(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{booking_id}", response_model=MessageResponse)
def cancel(booking_id: int, authorization: str | None = Header(default=None)):
    try:
        # (Optional) You can enforce “only owner can cancel” later
        require_user_id(authorization)
        cancel_booking(booking_id)
        return MessageResponse(message="Booking cancelled successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=BookingListResponse)
def my_bookings(authorization: str | None = Header(default=None)):
    try:
        user_id = require_user_id(authorization)
        bookings = get_user_bookings(user_id)
        return BookingListResponse(bookings=bookings)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/user/{user_id}", response_model=BookingListResponse)
def user_bookings(user_id: int):
    try:
        bookings = get_user_bookings(user_id)
        return BookingListResponse(bookings=bookings)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
