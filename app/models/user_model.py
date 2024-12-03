from sqlmodel import SQLModel,Field


class UserBase(SQLModel):
    phone_number: str = Field(max_length=11, regex="^09[0-9]{9}$",unique=True)
    otp_code: str = Field(max_length=6, regex="^[0-9]{6}$")

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)

class UserPublic(UserBase):
    id: int
    
class UserCreate(UserBase):
    pass