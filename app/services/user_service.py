from uuid import UUID
from click import echo
from fastapi import HTTPException
from starlette import status
from typing import TYPE_CHECKING, List
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from config import settings

from util.auth_utils import generate_password, get_password_hash
from db.schemas.user_schema import CreateUser, User, PatchUser
from db.models.user_model import User as UserModel


if TYPE_CHECKING:
    from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def create_user(user: CreateUser, db: "Session", current_user: UserModel) -> User:
    if current_user is None:
        raise settings.UNAUTHORIZED_ERROR

    db_user = UserModel(**user.model_dump())
    plain_password = generate_password(length=7)
    echo(f"@@ Generated password for user {db_user.email}: {plain_password}")
    db_user.password = get_password_hash(plain_password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # generate email def using {plain_password}

    except IntegrityError as e:
        db.rollback()
        # Check for unique constraint violation (email or phone number fields)
        if hasattr(e, "orig") and isinstance(e.orig, UniqueViolation):
            message = str(e.orig)

            if "phone_number" in message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Duplicate entry",
                        "message": f"A user with phone number ({db_user.phone_number}) already exists.",
                    }
                )
            elif "email" in message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Duplicate entry",
                        "message": f"A user with email ({db_user.email}) already exists.",
                    }
                )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return User.model_validate(db_user)


async def get_all_users(db: "Session", current_user: UserModel) -> List[User]:
    if current_user is None:
        raise settings.UNAUTHORIZED_ERROR

    try:
        db_users = db.query(UserModel).all()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return [User.model_validate(db_user) for db_user in db_users]


async def get_user(user_id: UUID, db: "Session", current_user: UserModel) -> User:
    if current_user is None:
        raise settings.UNAUTHORIZED_ERROR

    if current_user.id != user_id:
        raise settings.UNAUTHORIZED_ALTER_ERROR

    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return db_user


async def delete_user(user: UserModel, db: "Session", current_user: UserModel):
    if current_user is None:
        raise settings.UNAUTHORIZED_ERROR

    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"status": "success", "message": "User deleted successfully!"}


async def update_user(user_data: CreateUser, user: UserModel, db: "Session", current_user: UserModel) -> User:
    if current_user is None:
        raise settings.UNAUTHORIZED_ERROR

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


async def patch_user(user: UserModel, user_patch: PatchUser, db: "Session", current_user: UserModel) -> User:
    if current_user is None:
        raise settings.UNAUTHORIZED_ERROR

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

# async def get_user_by_email(email: str, db: "Session", current_user: UserModel):
#     if current_user is None:
#         raise settings.UNAUTHORIZED_ERROR

#     try:
#         db_user = db.query(UserModel).filter(UserModel.email == email).first()
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

#     return db_user
