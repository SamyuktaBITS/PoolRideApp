from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


UserType = Literal["campus", "guest"]


# -------- Common --------
class MessageResponse(BaseModel):
    message: str


# -------- Auth --------
class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    user_type: UserType
    email: Optional[str] = None
    phone: Optional[str] = None


class VerifyOTPRequest(BaseModel):
    user_id: int
    otp: str = Field(min_length=4, max_length=8)


class LoginRequest(BaseModel):
    # MVP login by email or phone (no password)
    email: Optional[str] = None
    phone: Optional[str] = None


class UserPublic(BaseModel):
    id: int
    name: str
    user_type: UserType
    is_verified: bool


class AuthResponse(BaseModel):
    user: UserPublic
    message: str
    dev_otp: Optional[str] = None  # only in DEV_MODE (for testing)


# -------- Rides --------
class RideCreateRequest(BaseModel):
    driver_id: Optional[int]=None
    from_text: str = Field(min_length=1, max_length=120)
    to_text: str = Field(min_length=1, max_length=120)
    depart_time: datetime
    seats_total: int = Field(ge=1, le=8)
    vehicle_type: str = Field(default="car", min_length=1, max_length=20)
    allow_guests: bool = False
    distance_km: float = Field(ge=0.5, le=200.0)


class RideResponse(BaseModel):
    id: int
    driver_id: int
    from_text: str
    to_text: str
    depart_time: datetime
    seats_total: int
    seats_left: int
    vehicle_type: str
    allow_guests: bool
    distance_km: float


class RideListResponse(BaseModel):
    rides: List[RideResponse]


# -------- Bookings --------
class BookingCreateRequest(BaseModel):
    ride_id: int
    rider_id: Optional[int]=None
    seats: int = Field(default=1, ge=1, le=4)


class BookingResponse(BaseModel):
    id: int
    ride_id: int
    rider_id: int
    seats: int
    status: str
    created_at: datetime
    co2_saved_kg_est: float
    drop_note: Optional[str] = None

    #useful fields for UI
    driver_id: Optional[int] = None
    from_text: Optional[str] = None
    to_text: Optional[str] = None
    depart_time: Optional[datetime] = None


class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]


# -------- Notifications --------
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    created_at: datetime
    is_read: bool


class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]


# -------- Ratings --------
class RatingCreateRequest(BaseModel):
    ride_id: int
    rater_id: Optional[int]=None
    driver_id: Optional[int]=None
    stars: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=300)


class RatingSummaryResponse(BaseModel):
    driver_id: int
    average_stars: float
    total_ratings: int


# -------- Profile --------
class UserProfileResponse(BaseModel):
    user: UserPublic
    rides_posted: int
    rides_taken: int
    total_co2_saved_kg: float
