from sqlmodel import SQLModel,Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, nullable=False)
    phone_number: str = Field(max_length=11, regex="^09[0-9]{9}$")
    otp_code: str = Field(max_length=6, regex="^[0-9]{6}$")
