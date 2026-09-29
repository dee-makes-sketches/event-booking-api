import asyncio
import httpx


BASE_URL = "http://127.0.0.1:8000"

EVENT_ID = 2
SEAT_ID = 8
SEAT_NUMBER = "A8"


USER_A = {
    "username": "case_d_user_a",
    "email": "case_d_user_a@gmail.com",
    "password": "password123"
}

USER_B = {
    "username": "case_d_user_b",
    "email": "case_d_user_b@gmail.com",
    "password": "password123"
}


# ============================================================
# REGISTER USER
# ============================================================

async def register_user(client, user):

    response = await client.post(
        "/auth/register",
        json=user
    )

    if response.status_code not in (200, 201, 400, 409):
        print(
            "Registration failed:",
            response.status_code,
            response.text
        )


# ============================================================
# LOGIN USER
# ============================================================

async def login_user(client, user):

    response = await client.post(
        "/auth/login",
        data={
            "username": user["email"],
            "password": user["password"]
        }
    )

    if response.status_code != 200:

        print(
            "Login failed:",
            response.status_code,
            response.text
        )

        return None

    return response.json()["access_token"]


# ============================================================
# GET SPECIFIC SEAT
# ============================================================

async def get_seat(client, event_id, seat_number, token):

    response = await client.get(
        f"/events/{event_id}/seats",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    if response.status_code != 200:

        print(
            "Could not fetch seats:",
            response.status_code,
            response.text
        )

        return None

    seats = response.json()

    for seat in seats:

        if seat["seat_number"] == seat_number:
            return seat

    return None


# ============================================================
# BOOK SEAT
# ============================================================

async def book_seat(client, token):

    response = await client.post(
        "/bookings",
        json={
            "event_id": EVENT_ID,
            "seat_id": SEAT_ID
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    return response


# ============================================================
# MAIN
# ============================================================

async def main():

    print("\n🔥 CASE D — TRANSACTION ROLLBACK 🔥\n")

    async with httpx.AsyncClient(
        base_url=BASE_URL
    ) as client:

        # ====================================================
        # 1. CREATE USERS
        # ====================================================

        print("Creating 2 customers...")

        await register_user(client, USER_A)
        await register_user(client, USER_B)

        print("Successfully created 2 users\n")


        # ====================================================
        # 2. LOGIN USERS
        # ====================================================

        print("Logging in 2 customers...")

        token_a = await login_user(
            client,
            USER_A
        )

        token_b = await login_user(
            client,
            USER_B
        )

        if not token_a or not token_b:

            print("❌ Login failed")

            return

        print("Successfully logged in 2 users\n")


        # ====================================================
        # 3. CHECK SEAT BEFORE BOOKING
        # ====================================================

        print("Checking seat BEFORE booking...")

        seat_before = await get_seat(
            client,
            EVENT_ID,
            SEAT_NUMBER,
            token_a
        )

        print(
            "Seat BEFORE:",
            seat_before
        )


        # ====================================================
        # 4. USER A ATTEMPTS BOOKING
        # ====================================================

        print("\nUser A attempting booking...")

        response_a = await book_seat(
            client,
            token_a
        )

        print(
            f"User A | Status: {response_a.status_code} | "
            f"{response_a.text}"
        )


        # ====================================================
        # 5. CHECK SEAT AFTER FAILED TRANSACTION
        # ====================================================

        print("\nChecking seat AFTER failed transaction...")

        seat_after = await get_seat(
            client,
            EVENT_ID,
            SEAT_NUMBER,
            token_a
        )

        print(
            "Seat AFTER:",
            seat_after
        )


        # ====================================================
        # 6. USER B ATTEMPTS SAME SEAT
        # ====================================================

        print("\nUser B attempting SAME seat...")

        response_b = await book_seat(
            client,
            token_b
        )

        print(
            f"User B | Status: {response_b.status_code} | "
            f"{response_b.text}"
        )


        # ====================================================
        # 7. SUMMARY
        # ====================================================
        print("\n========== SUMMARY ==========")

        if (
            response_a.status_code == 500
            and seat_after is not None
            and seat_after["status"].lower() == "available"
            and response_b.status_code == 200
        ):
            print("✅ CASE D PASSED")
            print("✅ User A transaction failed")
            print("✅ Rollback restored seat to AVAILABLE")
            print("✅ User B successfully booked the same seat")

        else:
            print("❌ CASE D FAILED")

            print("\nDebug information:")
            print("User A status:", response_a.status_code)
            print("Seat after:", seat_after)
            print("User B status:", response_b.status_code)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())