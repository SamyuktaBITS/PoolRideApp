from __future__ import annotations

import random
import flet as ft

from lib.api_client import ApiClient
from lib.session_store import save_session, load_session, clear_session
from lib.constants import APP_NAME, THEME_COLOR, ECO_QUOTES, ECO_FACTS
from lib.formatters import format_datetime


def main(page: ft.Page):
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 18
    page.bgcolor = "#F3FBF5"
    page.window.width = 980
    page.window.height = 640

    api = ApiClient()

    state = {
        "user_type": "campus",
        "name": "",
        "contact": "",
        "user_id": None,
        "token": None,
        "profile": None,
        "last_ride": None,
    }

    def snack(msg: str, ok: bool = True):
        sb = ft.SnackBar(
            content=ft.Text(msg, color="black"),
            bgcolor="#DFF7E1" if ok else "#FFE0E0",
            duration=6000,
        )
        page.overlay.append(sb)
        sb.open = True
        page.update()

    def set_view(content: ft.Control):
        page.controls.clear()
        page.add(content)
        page.update()

    def top_bar(title: str, show_actions: bool = False):
        actions = []
        if show_actions:
            actions = [
                ft.IconButton(icon=ft.icons.DIRECTIONS_CAR, tooltip="My Bookings", on_click=lambda e: show_bookings()),
                ft.IconButton(icon=ft.icons.NOTIFICATIONS_OUTLINED, tooltip="Notifications", on_click=lambda e: show_notifications()),
                ft.IconButton(icon=ft.icons.ACCOUNT_CIRCLE_OUTLINED, tooltip="Profile", on_click=lambda e: show_profile()),
            ]
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Row(actions, spacing=0),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            bgcolor=THEME_COLOR,
            border_radius=14,
        )

    def ensure_logged_in():
        if not state.get("token"):
            snack("Please login again.", ok=False)
            show_register()
            return False
        return True

    # ---------- AUTH / REGISTER ----------
    quote_text = ft.Text(random.choice(ECO_QUOTES), italic=True, color="#1F5E28")
    fact_text = ft.Text(random.choice(ECO_FACTS), size=12, color="#5A5A5A")

    def show_register():
        page.appbar = None

        name = ft.TextField(label="Your name", value=state["name"])
        contact = ft.TextField(label="Campus email or Guest phone/email", value=state["contact"])

        def select_type(t: str):
            state["user_type"] = t
            show_register()

        campus_btn = ft.ElevatedButton(
            text="🎓 Campus",
            bgcolor=THEME_COLOR if state["user_type"] == "campus" else "#E8F5E9",
            color="white" if state["user_type"] == "campus" else "#1B5E20",
            on_click=lambda e: select_type("campus"),
        )
        guest_btn = ft.ElevatedButton(
            text="👥 Guest",
            bgcolor=THEME_COLOR if state["user_type"] == "guest" else "#E8F5E9",
            color="white" if state["user_type"] == "guest" else "#1B5E20",
            on_click=lambda e: select_type("guest"),
        )

        def continue_login(_):
            state["name"] = name.value.strip()
            state["contact"] = contact.value.strip()

            if not state["name"]:
                snack("Please enter your name.", ok=False)
                return
            if not state["contact"]:
                snack("Please enter email/phone.", ok=False)
                return

            try:
                res = api.login(state["name"], state["contact"], state["user_type"])
                token = res.get("token")
                user = res.get("user") or {}
                if not token:
                    snack(f"Login failed. Response: {res}", ok=False)
                    return

                state["token"] = token
                state["user_id"] = user.get("id")

                save_session({
                    "token": token,
                    "name": state["name"],
                    "contact": state["contact"],
                    "user_type": state["user_type"],
                    "user_id": state["user_id"],
                })

                snack("Logged in ✅", ok=True)
                show_home()
            except Exception as ex:
                snack(f"Login failed: {ex}", ok=False)

        hero = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Ride together. Breathe better.", size=34, weight=ft.FontWeight.BOLD),
                    ft.Text("Campus carpools to the gate • Security handled at entry", color="#6B6B6B"),
                    ft.Container(height=10),
                    quote_text,
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=18,
            bgcolor="white",
            border_radius=22,
        )

        form = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Let’s get you onboard 🌱", size=16, weight=ft.FontWeight.BOLD),
                    name,
                    contact,
                    ft.Row([campus_btn, guest_btn], spacing=10),
                    ft.ElevatedButton(
                        text="Continue ✨",
                        bgcolor=THEME_COLOR,
                        color="white",
                        on_click=continue_login,
                        width=420,
                    ),
                ],
                spacing=12,
            ),
            padding=18,
            bgcolor="white",
            border_radius=22,
        )

        layout = ft.Column(
            [
                top_bar("🌿 PoolRide"),
                ft.Container(height=10),
                hero,
                ft.Container(height=12),
                form,
                ft.Container(height=12),
                ft.Container(content=fact_text, alignment=ft.alignment.center),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- HOME ----------
    def show_home():
        if not ensure_logged_in():
            return

        token = state["token"]

        try:
            prof = api.profile_me(token)
            state["profile"] = prof
        except Exception:
            state["profile"] = None

        user = (state["profile"] or {}).get("user") or {}
        name = user.get("name") or state.get("name") or "there"
        co2 = (state["profile"] or {}).get("total_co2_saved_kg")
        co2_txt = f"{co2:.3f} kg" if isinstance(co2, (int, float)) else "-- kg"

        post_enabled = (state.get("user_type") == "campus")

        def logout(_):
            try:
                api.logout(token)
            except Exception:
                pass
            clear_session()
            state["token"] = None
            state["profile"] = None
            snack("Logged out.", ok=True)
            show_register()

        layout = ft.Column(
            [
                top_bar("Home", show_actions=True),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Welcome, {name} 🌍", size=26, weight=ft.FontWeight.BOLD),
                            ft.Text(f"CO₂ saved so far: {co2_txt}", size=18, color="#1F5E28"),
                            ft.Text("🍃 Every shared ride is cleaner air.", color="#6B6B6B"),
                            ft.Container(height=10),
                            ft.Text(random.choice(ECO_QUOTES), italic=True, color="#1F5E28"),
                        ],
                        spacing=6,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Quick actions ⚡", size=16, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                text="🚗 Post a Ride (Campus only)",
                                disabled=not post_enabled,
                                bgcolor=THEME_COLOR if post_enabled else "#C8E6C9",
                                color="white" if post_enabled else "#2E7D32",
                                on_click=lambda e: show_post_ride(),
                                width=420,
                            ),
                            ft.ElevatedButton(
                                text="🔍 Find a Ride",
                                bgcolor=THEME_COLOR,
                                color="white",
                                on_click=lambda e: show_find_ride(),
                                width=420,
                            ),
                            ft.ElevatedButton(
                                text="📦 My Bookings",
                                bgcolor=THEME_COLOR,
                                color="white",
                                on_click=lambda e: show_bookings(),
                                width=420,
                            ),
                            ft.Row(
                                [
                                    ft.TextButton("Refresh Impact 🌱", on_click=lambda e: show_home()),
                                    ft.TextButton("Logout", on_click=logout),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
                ft.Container(height=10),
                ft.Container(content=ft.Text(random.choice(ECO_FACTS), size=12, color="#5A5A5A"), alignment=ft.alignment.center),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- POST RIDE ----------
    def show_post_ride():
        if not ensure_logged_in():
            return

        if state.get("user_type") != "campus":
            snack("Only campus users can post rides.", ok=False)
            show_home()
            return

        from_tf = ft.TextField(label="From (e.g., Campus Gate)")
        to_tf = ft.TextField(label="To (e.g., Hostel / City Center)")
        depart_tf = ft.TextField(label="Departure time (ISO)", value="2026-02-20T18:30:00")
        seats_tf = ft.TextField(label="Seats total (1-8)", value="3")
        dist_tf = ft.TextField(label="Distance (km)", value="5.0")
        vehicle_dd = ft.Dropdown(
            label="Vehicle type",
            options=[
                ft.dropdown.Option("car"),
                ft.dropdown.Option("scooter"),
                ft.dropdown.Option("van"),
            ],
            value="car",
        )
        allow_switch = ft.Switch(label="Allow guest bookings", value=False)

        def do_post(_):
            try:
                payload = {
                    "from_text": from_tf.value.strip(),
                    "to_text": to_tf.value.strip(),
                    "depart_time": depart_tf.value.strip(),
                    "seats_total": int(seats_tf.value.strip()),
                    "vehicle_type": (vehicle_dd.value or "car").strip(),
                    "allow_guests": bool(allow_switch.value),
                    "distance_km": float(dist_tf.value.strip()),
                }
                if not payload["from_text"] or not payload["to_text"]:
                    snack("From/To cannot be empty.", ok=False)
                    return

                res = api.post_ride(payload, token=state["token"])
                state["last_ride"] = res
                snack("Ride posted ✅", ok=True)
                show_ride_detail(int(res["id"]))
            except Exception as ex:
                snack(f"Post ride failed: {ex}", ok=False)

        layout = ft.Column(
            [
                top_bar("Post a Ride", show_actions=True),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Create your ride 🚗", size=18, weight=ft.FontWeight.BOLD),
                            from_tf,
                            to_tf,
                            depart_tf,
                            seats_tf,
                            vehicle_dd,
                            allow_switch,
                            dist_tf,
                            ft.Row(
                                [
                                    ft.ElevatedButton("Back", on_click=lambda e: show_home()),
                                    ft.ElevatedButton("Post", bgcolor=THEME_COLOR, color="white", on_click=do_post),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- SEARCH ----------
    def show_find_ride():
        if not ensure_logged_in():
            return

        from_tf = ft.TextField(label="From (e.g., Campus Gate)", autofocus=True)
        to_tf = ft.TextField(label="To (e.g., Hostel / City Center)")
        results_col = ft.Column(spacing=10)
        loading = ft.ProgressRing(visible=False)

        def render_results(rides):
            results_col.controls.clear()
            if not rides:
                results_col.controls.append(
                    ft.Container(
                        content=ft.Text("No rides found for this route 😕", color="#6B6B6B"),
                        padding=12,
                        bgcolor="white",
                        border_radius=14,
                    )
                )
                page.update()
                return

            for r in rides:
                ride_id = r.get("id")
                subtitle = f"🕒 {r.get('depart_time','--')} • Seats: {r.get('seats_left','--')} • 🚘 {r.get('vehicle_type','--')}"
                extra = []
                extra.append("Guests ✅" if r.get("allow_guests") else "Guests ❌")
                dist = r.get("distance_km")
                if isinstance(dist, (int, float)):
                    extra.append(f"{dist:.1f} km")

                card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"{r.get('from_text','--')} ➜ {r.get('to_text','--')}", size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(subtitle, size=12, color="#6B6B6B"),
                            ft.Text(" • ".join(extra), size=12, color="#1F5E28"),
                            ft.Row(
                                [
                                    ft.ElevatedButton(
                                        text="View",
                                        bgcolor=THEME_COLOR,
                                        color="white",
                                        on_click=lambda e, rid=ride_id: show_ride_detail(int(rid)),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=14,
                    bgcolor="white",
                    border_radius=18,
                )
                results_col.controls.append(card)

            page.update()

        def do_search(_):
            fq = (from_tf.value or "").strip()
            tq = (to_tf.value or "").strip()
            if not fq or not tq:
                snack("Please enter both From and To.", ok=False)
                return

            loading.visible = True
            page.update()
            try:
                res = api.search_rides(fq, tq)
                render_results(res.get("rides", []))
            except Exception as ex:
                snack(f"Search failed: {ex}", ok=False)
            finally:
                loading.visible = False
                page.update()

        layout = ft.Column(
            [
                top_bar("Find a Ride", show_actions=True),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Search rides 🔍", size=18, weight=ft.FontWeight.BOLD),
                            from_tf,
                            to_tf,
                            ft.Row(
                                [
                                    ft.ElevatedButton("Back", on_click=lambda e: show_home()),
                                    ft.ElevatedButton("Search", bgcolor=THEME_COLOR, color="white", on_click=do_search),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                        ],
                        spacing=10,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
                ft.Container(height=12),
                ft.Text("Results", size=14, weight=ft.FontWeight.BOLD),
                results_col,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- RIDE DETAIL + BOOK ----------
    def show_ride_detail(ride_id: int):
        if not ensure_logged_in():
            return

        loading = ft.ProgressRing(visible=True)
        title = ft.Text("Loading ride…", size=18, weight=ft.FontWeight.BOLD)
        body = ft.Column(spacing=8)

        seats_to_book = ft.TextField(label="Seats to book (1-4)", value="1", width=220)

        ride_holder = {"ride": None}

        def do_book(_):
            try:
                ride = ride_holder["ride"]
                if not ride:
                    snack("Ride not loaded.", ok=False)
                    return

                payload = {
                    "ride_id": int(ride["id"]),
                    "seats": int(seats_to_book.value.strip()),
                }
                res = api.book_ride(payload, token=state["token"])
                snack("Booked ✅", ok=True)
                show_bookings()
            except Exception as ex:
                snack(f"Booking failed: {ex}", ok=False)

        def load():
            try:
                ride = api.ride_detail(int(ride_id))
                ride_holder["ride"] = ride

                title.value = f"{ride.get('from_text','--')} ➜ {ride.get('to_text','--')}"
                body.controls.clear()
                body.controls.extend(
                    [
                        ft.Text(f"🕒 Departure: {ride.get('depart_time','--')}"),
                        ft.Text(f"🚘 Vehicle: {ride.get('vehicle_type','--')}"),
                        ft.Text(f"🪑 Seats: {ride.get('seats_left','--')} left / {ride.get('seats_total','--')} total"),
                        ft.Text(f"👤 Driver ID: {ride.get('driver_id','--')}"),
                        ft.Text("Guests allowed ✅" if ride.get("allow_guests") else "Guests not allowed ❌", color="#1F5E28"),
                    ]
                )
                dist = ride.get("distance_km")
                if isinstance(dist, (int, float)):
                    body.controls.append(ft.Text(f"📍 Distance: {dist:.1f} km"))

            except Exception as ex:
                snack(f"Ride detail failed: {ex}", ok=False)
            finally:
                loading.visible = False
                page.update()

        load()

        layout = ft.Column(
            [
                top_bar("Ride Details", show_actions=True),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            title,
                            body,
                            ft.Container(height=8),
                            ft.Row(
                                [
                                    seats_to_book,
                                    ft.ElevatedButton("Book", bgcolor=THEME_COLOR, color="white", on_click=do_book),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                            ft.TextButton("Back", on_click=lambda e: show_find_ride()),
                        ],
                        spacing=10,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- BOOKINGS ----------
    def show_bookings():
        if not ensure_logged_in():
            return

        results = ft.Column(spacing=10)
        loading = ft.ProgressRing(visible=True)

        def cancel(booking_id: int):
            try:
                api.cancel_booking(int(booking_id), token=state["token"])
                snack("Booking cancelled ✅", ok=True)
                show_bookings()
            except Exception as ex:
                snack(f"Cancel failed: {ex}", ok=False)

        def load():
            try:
                res = api.my_bookings(state["token"])
                bookings = res.get("bookings", [])

                results.controls.clear()
                if not bookings:
                    results.controls.append(ft.Text("No bookings yet.", color="#6B6B6B"))
                    return

                for b in bookings:
                    title = f"{b.get('from_text','--')} ➜ {b.get('to_text','--')}"
                    sub = f"🕒 {b.get('depart_time','--')} • Seats: {b.get('seats','--')} • Status: {b.get('status','--')}"
                    co2 = b.get("co2_saved_kg_est")
                    extra = f"🌱 CO₂ saved (est): {co2:.3f} kg" if isinstance(co2, (int, float)) else ""

                    btns = []
                    if b.get("status") == "CONFIRMED":
                        btns.append(
                            ft.TextButton(
                                "Cancel",
                                on_click=lambda e, bid=b.get("id"): cancel(int(bid)),
                            )
                        )
                        btns.append(
                            ft.TextButton(
                                "Rate",
                                on_click=lambda e, ride_id=b.get("ride_id"): show_rate_driver(int(ride_id)),
                            )
                        )

                    card = ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(title, weight=ft.FontWeight.BOLD),
                                ft.Text(sub, size=12, color="#6B6B6B"),
                                ft.Text(extra, size=12, color="#1F5E28"),
                                ft.Row(btns, alignment=ft.MainAxisAlignment.END),
                            ],
                            spacing=6,
                        ),
                        padding=14,
                        bgcolor="white",
                        border_radius=18,
                    )
                    results.controls.append(card)

            except Exception as ex:
                results.controls.clear()
                results.controls.append(ft.Text(f"Failed to load bookings: {ex}", color="red"))
            finally:
                loading.visible = False
                page.update()

        load()

        layout = ft.Column(
            [
                top_bar("My Bookings", show_actions=True),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Your booked rides 📦", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                            results,
                            ft.TextButton("Back", on_click=lambda e: show_home()),
                        ],
                        spacing=10,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- NOTIFICATIONS ----------
    def show_notifications():
        if not ensure_logged_in():
            return

        results = ft.Column(spacing=10)
        loading = ft.ProgressRing(visible=True)

        def mark_read(nid: int):
            try:
                api.mark_notification_read(nid, token=state["token"])
                snack("Marked as read ✅", ok=True)
                show_notifications()
            except Exception as ex:
                snack(f"Mark read failed: {ex}", ok=False)

        def load():
            try:
                res = api.my_notifications(state["token"])
                notifs = res.get("notifications", [])

                results.controls.clear()
                if not notifs:
                    results.controls.append(ft.Text("No notifications.", color="#6B6B6B"))
                    return

                for n in notifs:
                    title = n.get("title", "--")
                    body = n.get("body", "")
                    is_read = n.get("is_read", False)
                    nid = int(n.get("id"))

                    card = ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(("✅ " if is_read else "🔔 ") + title, weight=ft.FontWeight.BOLD),
                                ft.Text(body, size=12, color="#6B6B6B"),
                                ft.Row(
                                    [
                                        ft.TextButton(
                                            "Mark read" if not is_read else "Read",
                                            on_click=(lambda e, x=nid: mark_read(x)) if not is_read else None,
                                            disabled=is_read,
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=14,
                        bgcolor="white",
                        border_radius=18,
                    )
                    results.controls.append(card)

            except Exception as ex:
                results.controls.clear()
                results.controls.append(ft.Text(f"Failed to load notifications: {ex}", color="red"))
            finally:
                loading.visible = False
                page.update()

        load()

        layout = ft.Column(
            [
                top_bar("Notifications", show_actions=True),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Your updates 🔔", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
                            results,
                            ft.TextButton("Back", on_click=lambda e: show_home()),
                        ],
                        spacing=10,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- PROFILE ----------
    def show_profile():
        if not ensure_logged_in():
            return

        loading = ft.ProgressRing(visible=True)
        content = ft.Column(spacing=10)

        def load():
            try:
                prof = api.profile_me(state["token"])
                user = prof.get("user", {})
                uid = int(user.get("id"))

                rating = {}
                try:
                    rating = api.driver_rating_summary(uid)
                except Exception:
                    rating = {}

                content.controls.clear()
                content.controls.extend(
                    [
                        ft.Text("Profile 👤", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Name: {user.get('name','--')}"),
                        ft.Text(f"User type: {user.get('user_type','--')}"),
                        ft.Text(f"Verified: {user.get('is_verified', True)}"),
                        ft.Divider(),
                        ft.Text(f"Rides posted: {prof.get('rides_posted','--')}"),
                        ft.Text(f"Rides taken: {prof.get('rides_taken','--')}"),
                        ft.Text(f"Total CO₂ saved: {prof.get('total_co2_saved_kg','--')} kg", color="#1F5E28"),
                        ft.Divider(),
                        ft.Text(
                            f"Driver rating: {rating.get('average_stars','--')} ⭐ ({rating.get('total_ratings','--')} ratings)"
                        ),
                        ft.TextButton("Back", on_click=lambda e: show_home()),
                    ]
                )
            except Exception as ex:
                content.controls.clear()
                content.controls.append(ft.Text(f"Failed to load profile: {ex}", color="red"))
            finally:
                loading.visible = False
                page.update()

        load()

        layout = ft.Column(
            [
                top_bar("Profile", show_actions=True),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column([ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER), content], spacing=10),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- RATE DRIVER ----------
    def show_rate_driver(ride_id: int):
        if not ensure_logged_in():
            return

        stars = ft.Dropdown(
            label="Stars",
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            value="5",
        )
        comment = ft.TextField(label="Comment (optional)", multiline=True, min_lines=2, max_lines=4)

        def submit(_):
            try:
                payload = {
                    "ride_id": int(ride_id),
                    "stars": int(stars.value),
                    "comment": (comment.value or "").strip() or None,
                }
                api.rate_driver(payload, token=state["token"])
                snack("Rating submitted ✅", ok=True)
                show_bookings()
            except Exception as ex:
                snack(f"Rating failed: {ex}", ok=False)

        layout = ft.Column(
            [
                top_bar("Rate Driver", show_actions=True),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"Rate ride #{ride_id}", size=18, weight=ft.FontWeight.BOLD),
                            stars,
                            comment,
                            ft.Row(
                                [
                                    ft.ElevatedButton("Back", on_click=lambda e: show_bookings()),
                                    ft.ElevatedButton("Submit", bgcolor=THEME_COLOR, color="white", on_click=submit),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=18,
                    bgcolor="white",
                    border_radius=22,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        set_view(layout)

    # ---------- BOOT ----------
    sess = load_session()
    if sess and sess.get("token"):
        state["token"] = sess["token"]
        state["contact"] = sess.get("contact", "")
        state["name"] = sess.get("name", "")
        state["user_type"] = sess.get("user_type", "campus")
        state["user_id"] = sess.get("user_id")
        show_home()
    else:
        show_register()


ft.app(target=main)
