import asyncpg
from typing_extensions import Annotated

from fastapi import Depends

from sqlmodel import Session , create_engine,SQLModel

DATABASE_PASSWORD='13801121'
DATABASE_USER='madassandd'
DATABASE_HOST='localhost'
DATABASE_NAME='fast_store'
DATABASE_PATH='postgresql+psycopg2'

DATABASE_URL=f"{DATABASE_PATH}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URL,echo=True)


async def create_database_if_not_exists():
    from sqlalchemy.engine import URL
    # Parse the database URL
    database_name = DATABASE_NAME
    connection = await asyncpg.connect(
        user=DATABASE_USER, password=DATABASE_PASSWORD, database="postgres", host=DATABASE_HOST
    )
    exists = await connection.fetchval(
        f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'"
    )
    if not exists:
        print(f"Database '{database_name}' does not exist. Creating it...")
        await connection.execute(f"CREATE DATABASE {database_name}")
        print(f"Database '{database_name}' created successfully.")
    await connection.close()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep= Annotated[Session,Depends(get_session)]