import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import create_db_and_tables
from backend.routers import beers, food, wines


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

allowed_origins_raw = os.environ.get("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(wines.router)
app.include_router(beers.router)
app.include_router(food.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Static files mount LAST so /api/* routes take precedence
app.mount("/", StaticFiles(directory=".", html=True), name="static")
