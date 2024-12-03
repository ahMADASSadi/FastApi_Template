from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config.setting import create_db_and_tables, get_session
from app.routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app:FastAPI):
    create_db_and_tables()
    print("Database initialized!")
    yield
    print("Application shutting down!")
    


app = FastAPI(title="FastAPI store",lifespan=lifespan)


@app.get('/')
async def read_root():
    return {"message": "Welcome to the FastAPI store!"}

app.include_router(user_router)