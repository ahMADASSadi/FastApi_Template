from fastapi import Depends
from sqlmodel import Session , create_engine,SQLModel
from typing_extensions import Annotated

DATA_BASE_URL="postgresql://madassandd:13801121@localhost/fast_store"

engine = create_engine(DATA_BASE_URL,echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep= Annotated[Session,Depends(get_session)]