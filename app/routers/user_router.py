from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import select

from app.config.setting import SessionDep
from app.models.user_model import User ,UserPublic,UserCreate

router = APIRouter(prefix='/user',tags=['user'])
@router.get('/')
def read_users(session: SessionDep):
    try:
        users = session.exec(select(User)).all()
        return users
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e


@router.get('/{user_id}',response_model=UserPublic)
def read_user(user_id: int, session: SessionDep):
    try:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error") from e



@router.post('/create', response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    try:
        # Start a transaction block explicitly
        with session.begin():
            db_user = User(**user.model_dump())
            session.add(db_user)
            session.commit()  # Commit only if everything succeeds
            session.refresh(db_user)
        return db_user
    except IntegrityError as e:
        session.rollback()  # Roll back the transaction to prevent id increment
        raise HTTPException(status_code=400, detail="User already exists") from e
    except SQLAlchemyError as e:
        session.rollback()  # Roll back for any other database errors
        raise HTTPException(status_code=500, detail="Database error") from e
    except Exception as e:
        session.rollback()  # Roll back for unexpected errors
        raise HTTPException(status_code=500, detail="Unexpected error") from e