from uuid import UUID
from pydantic import BaseModel


class _BaseAuthRequest(BaseModel):
    email: str
    password: str


class AuthRequest(_BaseAuthRequest):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: UUID | None = None
