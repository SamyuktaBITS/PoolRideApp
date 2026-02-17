"""
PoolRide Backend - Main Entry Point

Responsibilities:
- Load environment variables
- Load application configuration
- Initialize database
- Register API routes
- Start FastAPI application
"""

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# App Initialization
# -------------------------------------------------
app = FastAPI(
    title="PoolRide Backend",
    description="Campus-focused carpooling backend with CO₂ tracking",
    version="1.0.0"
)

# -------------------------------------------------
# Configuration & Database Initialization
# -------------------------------------------------
from lib.settings import settings
from lib.db import init_db

init_db()

# -------------------------------------------------
# API Route Registration
# -------------------------------------------------
from api.routes_auth import router as auth_router
from api.routes_rides import router as rides_router
from api.routes_bookings import router as bookings_router
from api.routes_notifications import router as notifications_router
from api.routes_ratings import router as ratings_router
from api.routes_profile import router as profile_router

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(rides_router, prefix="/rides", tags=["Rides"])
app.include_router(bookings_router, prefix="/bookings", tags=["Bookings"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(ratings_router, prefix="/ratings", tags=["Ratings"])
app.include_router(profile_router, prefix="/profile", tags=["Profile"])

# -------------------------------------------------
# Health Check Endpoint
# -------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "OK",
        "app": settings.APP_NAME,
        "environment": settings.ENVIRONMENT
    }

# -------------------------------------------------
# Startup Log (for clarity)
# -------------------------------------------------
@app.on_event("startup")
def on_startup():
    print("🌱 PoolRide Backend is starting...")
    print(f"Environment : {settings.ENVIRONMENT}")
    print(f"Database    : {settings.DB_TYPE}")
