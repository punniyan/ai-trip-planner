# app/main.py

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.api.trip import router as trip_router


app = FastAPI(
    title="AI Trip Planner",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=[
        "*",
    ],
    allow_headers=[
        "*",
    ],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(
    trip_router
)


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
async def root():

    return {
        "status": "ok",
        "message": "AI Trip Planner API is running",
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy",
    }