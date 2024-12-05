from fastapi_cli import cli as fast_api_cli
import uvicorn
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import FastAPI
from app.config.setting import create_db_and_tables, get_session, create_database_if_not_exists
from app.routers.user_router import router as user_router
from contextlib import asynccontextmanager


# Utility to run subprocess commands safely
def run_subprocess(command: list[str]) -> None:
    try:
        result = subprocess.run(command, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running command: {e.stderr.decode()}")
        raise


# Function to handle Alembic migrations
def make_migrations(option: Optional[str] = None) -> None:
    from app.config.setting import DATABASE_URL

    alembic_dir = Path("app/config/migrations")
    config_dir = Path("app/config")
    alembic_ini_path = config_dir / "alembic.ini"
    env_py_path = alembic_dir / "env.py"

    # Step 1: Initialize Alembic if migrations folder doesn't exist
    if not alembic_dir.exists():
        print("Initializing Alembic...")
        run_subprocess(["alembic", "init", str(alembic_dir)])

        # Move alembic.ini to app/config
        default_alembic_ini = Path("alembic.ini")
        if default_alembic_ini.exists():
            default_alembic_ini.rename(alembic_ini_path)
            print(f"Moved alembic.ini to {alembic_ini_path}")
        else:
            print("Error: alembic.ini file not found after initialization.")
            return

        print("Alembic initialized.")

    # Step 2: Update alembic.ini with the correct DATABASE_URL
    if alembic_ini_path.exists():
        alembic_ini_content = alembic_ini_path.read_text()
        alembic_ini_content = alembic_ini_content.replace(
            "script_location = app/config/migrations", "script_location = app/config/migrations"
        )
        alembic_ini_content = alembic_ini_content.replace(
            "sqlalchemy.url = driver://user:pass@localhost/dbname", f"sqlalchemy.url = {
                DATABASE_URL}"
        )
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

    # Step 5: Handle migration or makemigrations based on the option
    if option == "makemigrations":
        run_subprocess(["alembic", "-c", str(alembic_ini_path),
                       "revision", "--autogenerate", "-m", f'"{datetime.now().strftime('%Y-%m-%d:%H:%M')}"'])
        print("Finished making migrations!")
    elif option == "migrate":
        run_subprocess(
            ['alembic', "-c", str(alembic_ini_path), 'upgrade', 'head'])
        print("All migrations are done!")


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
app.include_router(user_router)


@app.get('/')
async def read_root():
    return {"message": "Welcome to the FastAPI store!"}


# Main entry point for the app and migration handling
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "makemigrations":
            make_migrations("makemigrations")
        elif command == "migrate":
            make_migrations("migrate")
        else:
            print(f"Unknown command: {command}")
    else:
        # fast_api_cli.dev('app')
        # This is where the app would run during development
        uvicorn.run(app, host='0.0.0.0', port=8000)
