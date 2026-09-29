import asyncio
import uuid
import httpx


BASE_URL = "http://127.0.0.1:8000"

EVENT_ID = 2
PASSWORD = "password123"


# ============================================================
# USER HELPERS
# ============================================================

async def create_user(client, number):
    unique = uuid.uuid4().hex[:8]

    username = f"test_user_{number}_{unique}"
    email = f"{username}@gmail.com"

    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": PASSWORD,
            "role": "customer"
        }
    )

    if response.status_code != 201:
        print(
            f"USER {number} CREATION FAILED:",
            response.status_code,
            response.text
        )
        return None

    return {
        "email": email,
        "password": PASSWORD
    }


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
            "LOGIN FAILED:",
            response.status_code,
            response.text
        )
        return None

    return response.json()["access_token"]


# ============================================================
# TEST USER SETUP
# ============================================================

async def create_and_login_users(client, count):
    print(f"\nCreating {count} customers...\n")

    users = await asyncio.gather(
        *(create_user(client, i) for i in range(count))
    )

    users = [user for user in users if user is not None]

    print(f"Successfully created {len(users)} users")


    print(f"\nLogging in {len(users)} customers...\n")

    tokens = await asyncio.gather(
        *(login_user(client, user) for user in users)
    )

    tokens = [token for token in tokens if token is not None]

    print(f"Successfully logged in {len(tokens)} users")

    return tokens


# ============================================================
# BOOKING HELPER
# ============================================================

async def book_seat(client, token, event_id, seat_id, request_number):
    response = await client.post(
        "/bookings",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "event_id": event_id,
            "seat_id": seat_id
        }
    )

    return {
        "request": request_number,
        "seat_id": seat_id,
        "status": response.status_code,
        "response": response.text
    }


# ============================================================
# RESULT PRINTER
# ============================================================

def print_results(results):
    print("\n========== RESULTS ==========\n")

    success_count = 0

    for result in results:

        print(
            f"Request {result['request']:2} | "
            f"Seat: {result['seat_id']} | "
            f"Status: {result['status']} | "
            f"{result['response']}"
        )

        if result["status"] in [200, 201]:
            success_count += 1


    print("\n========== SUMMARY ==========")

    print(f"Total requests: {len(results)}")
    print(f"Successful bookings: {success_count}")
    print(f"Failed bookings: {len(results) - success_count}")

    return success_count


# ============================================================
# CASE A
# SAME SEAT CONCURRENTLY
#
# Expected:
# 1 success
# Remaining -> 409
# ============================================================

async def case_a_same_seat_concurrent(client):

    SEAT_ID = 1
    USER_COUNT = 20

    print("\n🔥 CASE A — SAME SEAT CONCURRENTLY 🔥")
    print(f"{USER_COUNT} users trying to book Seat {SEAT_ID}")

    tokens = await create_and_login_users(
        client,
        USER_COUNT
    )

    results = await asyncio.gather(
        *(
            book_seat(
                client,
                token,
                EVENT_ID,
                SEAT_ID,
                i
            )
            for i, token in enumerate(tokens)
        )
    )

    success_count = print_results(results)

    print("\nEXPECTED: Exactly 1 successful booking")

    if success_count == 1:
        print("✅ CASE A PASSED")
    else:
        print("❌ CASE A FAILED")


# ============================================================
# CASE B
# DIFFERENT SEATS CONCURRENTLY
#
# Expected:
# ALL succeed
#
# Important:
# Replace seat IDs with actual AVAILABLE seat IDs
# ============================================================

async def case_b_different_seats(client):

    SEAT_IDS = [2, 3, 4]

    print("\n🔥 CASE B — DIFFERENT SEATS CONCURRENTLY 🔥")

    tokens = await create_and_login_users(
        client,
        len(SEAT_IDS)
    )

    print(
        f"\n{len(tokens)} users booking different seats "
        f"at the same time\n"
    )

    results = await asyncio.gather(
        *(
            book_seat(
                client,
                token,
                EVENT_ID,
                seat_id,
                i
            )
            for i, (token, seat_id)
            in enumerate(zip(tokens, SEAT_IDS))
        )
    )

    success_count = print_results(results)

    print(
        f"\nEXPECTED: {len(SEAT_IDS)} successful bookings"
    )

    if success_count == len(SEAT_IDS):
        print("✅ CASE B PASSED")
    else:
        print("❌ CASE B FAILED")


# ============================================================
# CASE C
# SAME SEAT SEQUENTIALLY
#
# Expected:
# User A -> success
# User B -> 409
# ============================================================

async def case_c_same_seat_sequential(client):

    SEAT_ID = 5

    print("\n🔥 CASE C — SAME SEAT SEQUENTIALLY 🔥")

    tokens = await create_and_login_users(
        client,
        2
    )

    print("\nUser A booking seat...")

    result_a = await book_seat(
        client,
        tokens[0],
        EVENT_ID,
        SEAT_ID,
        1
    )

    print(
        f"User A | "
        f"Status: {result_a['status']} | "
        f"{result_a['response']}"
    )


    print("\nUser B booking SAME seat...")

    result_b = await book_seat(
        client,
        tokens[1],
        EVENT_ID,
        SEAT_ID,
        2
    )

    print(
        f"User B | "
        f"Status: {result_b['status']} | "
        f"{result_b['response']}"
    )


    print("\n========== SUMMARY ==========")

    if (
        result_a["status"] in [200, 201]
        and result_b["status"] == 409
    ):
        print("✅ CASE C PASSED")
    else:
        print("❌ CASE C FAILED")


# ============================================================
# MAIN
# ============================================================

async def main():

    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=30
    ) as client:

        # Uncomment whichever test you want

        # await case_a_same_seat_concurrent(client)

         await case_b_different_seats(client)

        #await case_c_same_seat_sequential(client)


if __name__ == "__main__":
    asyncio.run(main())