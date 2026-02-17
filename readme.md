# 🌱 PoolRide – Campus Carpooling Platform

PoolRide is a **campus-focused carpooling platform** designed to reduce single-occupancy commuting and promote sustainable travel around university campuses.

The system enables verified campus users to post rides and allows both campus and guest users to book available seats. Each shared ride visibly tracks **CO₂ emission savings**, reinforcing eco-conscious commuting.

> PoolRide does not manage campus entry permissions. Drop-offs are handled at the campus gate as per institutional security policies.

---

# 🎯 Project Vision

- Reduce carbon footprint from daily commuting  
- Encourage collaborative campus transportation  
- Make environmental impact measurable and visible  
- Provide a lightweight, privacy-friendly ride-sharing MVP  

---

# 👥 User Roles

## 🎓 Campus Users
- Login using campus-approved email  
- Can:
  - Post rides  
  - Book rides  
  - Receive ratings  
  - View impact summary  

## 👥 Guest Users
- Login using phone or email  
- Can:
  - Search and book rides  
  - View personal CO₂ savings  
- Drop-off restricted to campus gate (as per policy)  

---

# 🚗 Features Implemented (Final Version)

## 🔐 Authentication
- One-tap login (auto create or login)
- Token-based session management
- Local session persistence (mobile app)

---

## 🚘 Ride Management
- Campus users can post rides
- Ride search by origin & destination
- View detailed ride information
- Seat availability tracking
- Guest booking restrictions supported

---

## 📦 Booking System
- Instant booking
- Seat deduction logic
- Booking cancellation
- CO₂ savings estimation per booking
- Drop policy notes for guest users

---

## 🌍 CO₂ Impact Tracking

For every confirmed booking, PoolRide calculates:

Solo emission = distance × emission factor  
Shared emission per passenger = solo emission ÷ total passengers  
CO₂ saved = solo − shared per passenger  

Emission factors are configurable per vehicle type:

| Vehicle  | kg CO₂ / km |
|----------|-------------|
| Car      | 0.21        |
| Scooter  | 0.10        |
| Van      | 0.30        |

Impact is shown:
- Per booking  
- In user profile summary  
- On home dashboard  

---

# 🔔 Notifications
- Ride posted confirmation
- Booking confirmed alerts
- New rating alerts
- Booking cancellation notifications

---

# ⭐ Driver Ratings
- Riders can rate drivers after booking
- Average rating calculation
- Rating summary endpoint

---

# 👤 Profile Dashboard
- Rides posted
- Rides taken
- Total CO₂ saved
- Rating summary (via ratings endpoint)

---

# 🏗️ System Architecture

## Backend
- Python
- FastAPI
- SQLite (MVP database)
- Configurable via JSON + environment variables
- Token-based session storage

## Mobile App
- Python
- Flet UI framework
- REST API integration
- Local session storage
- Eco-themed user experience

---

# 🗄️ Database Schema (MVP)

Tables:
- Users
- Rides
- Bookings
- Notifications
- Ratings
- Sessions

---

# 🌿 Sustainability Model

PoolRide uses a **distance-based emission factor model** to estimate avoided CO₂ emissions.

Assumptions:
- Solo commute is baseline
- Emissions are divided among total passengers in shared ride
- Saved emissions are displayed to user

The model is simple, transparent, and configurable for future upgrades.

---

# ⚠️ Out of Scope (MVP)

- No live GPS tracking
- No payment gateway
- No wallet system
- No dynamic pricing
- No campus ID validation system
- No in-app chat

---

# 🚀 Running the Project

## Backend

## python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 in /backend
## python main.py in /mobile_app