from __future__ import annotations

import requests
from typing import Any, Dict, Optional
from .constants import API_BASE


class ApiClient:
    def __init__(self, base_url: str = API_BASE, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    def login(self, name: str, contact: str, user_type: str) -> Dict[str, Any]:
        payload = {"name": name, "contact": contact, "user_type": user_type}
        r = requests.post(self._url("/auth/login"), json=payload, timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def logout(self, token: str) -> Dict[str, Any]:
        r = requests.post(self._url("/auth/logout"), headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def profile_me(self, token: str) -> Dict[str, Any]:
        r = requests.get(self._url("/profile/me"), headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    # ---------- RIDES ----------
    def search_rides(self, from_q: str, to_q: str) -> Dict[str, Any]:
        params = {"from_q": from_q, "to_q": to_q}
        r = requests.get(self._url("/rides/search"), params=params, timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def ride_detail(self, ride_id: int) -> Dict[str, Any]:
        r = requests.get(self._url(f"/rides/{ride_id}"), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def post_ride(self, payload: Dict[str, Any], token: str) -> Dict[str, Any]:
        r = requests.post(self._url("/rides/"), json=payload, headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    # ---------- BOOKINGS ----------
    def book_ride(self, payload: Dict[str, Any], token: str) -> Dict[str, Any]:
        r = requests.post(self._url("/bookings/"), json=payload, headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def my_bookings(self, token: str) -> Dict[str, Any]:
        r = requests.get(self._url("/bookings/me"), headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def cancel_booking(self, booking_id: int, token: str) -> Dict[str, Any]:
        r = requests.delete(self._url(f"/bookings/{booking_id}"), headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    # ---------- NOTIFICATIONS ----------
    def my_notifications(self, token: str) -> Dict[str, Any]:
        r = requests.get(self._url("/notifications/me"), headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def mark_notification_read(self, notification_id: int, token: str) -> Dict[str, Any]:
        r = requests.post(self._url(f"/notifications/{notification_id}/read"), headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    # ---------- RATINGS ----------
    def rate_driver(self, payload: Dict[str, Any], token: str) -> Dict[str, Any]:
        r = requests.post(self._url("/ratings/"), json=payload, headers=self._headers(token), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()

    def driver_rating_summary(self, driver_id: int) -> Dict[str, Any]:
        r = requests.get(self._url(f"/ratings/driver/{driver_id}"), timeout=self.timeout)
        if r.status_code >= 400:
            raise ValueError(f"{r.status_code} {r.text}")
        return r.json()
