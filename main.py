from fastapi import FastAPI
from api.auth import router as auth_router
from api.user import router as users_router
from api.test import router as test_router
from api.venue import router as venue_router
from api.event import router as event_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(test_router)
app.include_router(venue_router)
app.include_router(event_router)

@app.get("/health")
def health():
    return {"status" : "ok"}

