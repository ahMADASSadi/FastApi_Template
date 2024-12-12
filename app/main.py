import sys
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.config.setting import create_db_and_tables, get_session, create_database_if_not_exists, SESSION_DEPENDENCY, get_engine
from app.admin.admin_router import router as admin_router
from app.cli import commands

# Utility to run subprocess commands safely


# Asynchronous context manager for managing lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_database_if_not_exists()
    create_db_and_tables()
    print("Database initialized!")
    yield
    print("Application shutting down!")


# FastAPI app setup
app = FastAPI(title="FastAPI store", lifespan=lifespan)


@app.get('/')
async def read_root():
    return {"message": "Welcome to the FastAPI!"}

app.include_router(admin_router)

# Main entry point for the app and migration handling
if __name__ == "__main__":
    """
    If length of the enterd argument is greater than 1
    """
    if len(sys.argv) > 1:
        command = sys.argv[1]
        commands(command)
    else:
        """
        for running the app using the uvicorn and in the production mode rather than the FastAPI built-in command (fastapi run)
        """
        # fast_api_cli.dev('app')
        # This is where the app would run during development
        uvicorn.run(app, host='0.0.0.0', port=8000)
