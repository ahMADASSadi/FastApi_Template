from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.config.setting import SessionDep
from app.models.user_model import User
router = APIRouter(prefix='/user',tags=['user'])

@router.get('/')
def read_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users

@router.get('/{user_id}',response_model=User)
def read_user(user_id:int,session:SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post('/create',response_model=User)
def create_user(user:User,session:SessionDep):
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user