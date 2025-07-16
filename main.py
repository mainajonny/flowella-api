from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import auth_router, user_router
from app.util.init_db import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init the db at start
    create_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Flowella API",
    description="A FastAPI application for flowella APIs.",
    version="0.1.0",
)

# Register routes
app.include_router(auth_router.router)
app.include_router(user_router.router)


@app.get('/')
def read_root():
    return {"status": "Flowella api running..."}
