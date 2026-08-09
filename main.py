from fastapi import FastAPI
from api.auth import router as auth_router
from api.users import router as users_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)



@app.get("/health")
def health():
    return {"status" : "ok"}