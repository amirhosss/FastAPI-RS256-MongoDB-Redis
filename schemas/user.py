from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from core.config import settings


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=settings.STR_MAX_LENGTH)
    last_name: str = Field(..., max_length=settings.STR_MAX_LENGTH)
    email: EmailStr
    password: str = Field(..., regex=settings.PASSWORD_REGEX)


class UserOut(BaseModel):
    first_name: str
    last_name: str
    email: str
    is_active: bool
    is_superuser: bool


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=settings.STR_MAX_LENGTH)
    last_name: Optional[str] = Field(None, max_length=settings.STR_MAX_LENGTH)