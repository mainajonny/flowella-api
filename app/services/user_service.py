
import string as _s
import pdb

from random import choices
from uuid import UUID
from fastapi import HTTPException
from starlette import status
from typing import TYPE_CHECKING, List
from passlib.context import CryptContext
from psycopg2.errors import UniqueViolation

from db.schemas.user_schema import CreateUser, User, PatchUser
from db.models import user_model


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def generate_password(length=7):
    chars = _s.ascii_letters + _s.digits
    return ''.join(choices(chars, k=length))


def hash_password(password: str):
    hashed_password = pwd_context.hash(password)
    return hashed_password


async def create_user(user: CreateUser, db: "Session") -> User:
    db_user = user_model.User(**user.model_dump())
    plain_password = generate_password()
    db_user.password = hash_password(plain_password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # generate email def using {plain_password}
    except Exception as e:
        db.rollback()
        # Check for unique constraint violation (email or other unique fields)

        pdb.set_trace()

        if hasattr(e, 'orig') and isinstance(e.orig, UniqueViolation):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return User.model_validate(db_user)


async def get_all_users(db: "Session") -> List[User]:
    try:
        db_users = db.query(user_model.User).all()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return [User.model_validate(db_user) for db_user in db_users]


async def get_user(user_id: UUID, db: "Session"):
    try:
        db_user = db.query(user_model.User).filter(
            user_model.User.id == user_id).first()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return db_user


async def get_user_by_email(email: str, db: "Session"):
    try:
        db_user = db.query(user_model.User).filter(
            user_model.User.email == email).first()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return db_user


async def delete_user(user: user_model.User, db: "Session"):
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"status": "success", "message": "User deleted successfully!"}


async def update_user(user_data: CreateUser, user: user_model.User, db: "Session") -> User:
    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.email = user_data.email
    user.phone_number = user_data.phone_number

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return User.model_validate(user)


async def patch_user(user: user_model.User, user_patch: PatchUser, db: "Session") -> User:
    for field, value in user_patch.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return User.model_validate(user)
