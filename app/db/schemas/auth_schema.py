from pydantic import BaseModel


class AuthRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
