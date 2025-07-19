from fastapi import APIRouter

from core.database import db_dependancy
from db.schemas.auth_schema import AuthRequest, Token
from services import auth_service as _service


router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/token", response_model=Token)
async def authenticate_user(user: AuthRequest, db: db_dependancy) -> Token:
    return await _service.authenticate_user(user=user, db=db)
