import sys
import os
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI

import uvicorn

from app.config.setting import create_db_and_tables, get_session,create_database_if_not_exists
from app.routers.user_router import router as user_router


def make_migrations(option:Optional[str]=None) -> None:
    from app.config.setting import DATABASE_URL
    
    """Ensure Alembic is initialized and properly configured."""
    alembic_dir = Path("app/config/migrations")
    config_dir = Path("app/config")
    alembic_ini_path = config_dir / "alembic.ini"
    env_py_path = alembic_dir / "env.py"

    # Step 1: Initialize Alembic if migrations folder doesn't exist
    if not alembic_dir.exists():
        print("Initializing Alembic...")
        subprocess.run(["alembic", "init", str(alembic_dir)])

        # Move alembic.ini to app/config
        default_alembic_ini = Path("alembic.ini")
        if default_alembic_ini.exists():
            default_alembic_ini.rename(alembic_ini_path)
            print(f"Moved alembic.ini to {alembic_ini_path}")
        else:
            print("Error: alembic.ini file not found after initialization.")
            return

        print("Alembic initialized.")

    # Step 2: Add database URL to alembic.ini
    if alembic_ini_path.exists():
        alembic_ini_content = alembic_ini_path.read_text()

        # Fix `script_location` to point to the `migrations` directory only
        alembic_ini_content = alembic_ini_content.replace(
            "script_location = app/config/migrations",  # Default location
            "script_location = app/config/migrations"
        )

        # Update `sqlalchemy.url` with DATABASE_URL from settings
        alembic_ini_content = alembic_ini_content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname", 
            f"sqlalchemy.url = {DATABASE_URL}"
        )

        # Write the updated alembic.ini
        alembic_ini_path.write_text(alembic_ini_content)
        print(f"Updated {alembic_ini_path} with the correct values.")

    # Step 3: Ensure __init__.py files exist
    for directory in [config_dir, alembic_dir]:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"Created {init_file}")

    # Step 4: Update env.py to use SQLModel
    if env_py_path.exists():
        with open(env_py_path, "r") as f:
            env_py_content = f.read()
        if "target_metadata" not in env_py_content or "SQLModel" not in env_py_content:
            updated_env_py = env_py_content.replace(
                "from alembic import context",
                "from alembic import context\nfrom sqlmodel import SQLModel",
            )
            updated_env_py = updated_env_py.replace(
                "target_metadata = None",
                "target_metadata = SQLModel.metadata",
            )
            with open(env_py_path, "w") as f:
                f.write(updated_env_py)
            print(f"Updated {env_py_path} to use SQLModel.")
    
    if option=="makemigrations":
        subprocess.run(["alembic", "-c", str(alembic_ini_path), "revision", "--autogenerate", "-m", f'"{datetime.now()}"'])
    elif option=="migrate":
        subprocess.run(['alembic', "-c", str(alembic_ini_path),'upgrade','head'])




@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_database_if_not_exists()
    create_db_and_tables()
    print("Database initialized!")
    yield
    print("Application shutting down!")
    

app = FastAPI(title="FastAPI store",lifespan=lifespan)


@app.get('/')
async def read_root():
    return {"message": "Welcome to the FastAPI store!"}

app.include_router(user_router)



if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] =="makemigrations":
        make_migrations("makemigrations")
    elif len(sys.argv) > 1 and sys.argv[1] == "migrate":
        make_migrations("migrate")
    else:
        uvicorn.run(app, host='0.0.0.0', port=8000)