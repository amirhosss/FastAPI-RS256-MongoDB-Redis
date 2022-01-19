from datetime import datetime

from pydantic import BaseModel


class UserInDB(BaseModel):
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    created_at: datetime
    is_active: bool
    is_superuser: bool


class User(UserInDB):
    public_id: str