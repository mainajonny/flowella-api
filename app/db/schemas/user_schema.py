from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class _BaseUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None


class CreateUser(_BaseUser):
    pass


class PatchUser(_BaseUser):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: Optional[str] | None = None


class User(_BaseUser):
    id: UUID
    is_active: bool
    created_at: datetime
    password: str = Field(exclude=True)

    class Config:
        from_attributes = True
