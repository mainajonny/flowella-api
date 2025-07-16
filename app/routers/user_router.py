from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException
from starlette import status
from sqlalchemy import select

from core.database import db_dependancy
from db.schemas.user_schema import User, CreateUser, PatchUser
from db.models import user_model
from services import user_service as _service
from config import settings

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/", response_model=User)
async def create_user(user: CreateUser, db: db_dependancy):
    return await _service.create_user(user=user, db=db)


@router.get("/", response_model=List[User])
async def get_users(db: db_dependancy):
    return await _service.get_all_users(db=db)


@router.get("/{user_id}/", response_model=User)
async def get_user(user_id: UUID, db: db_dependancy):
    request_user = await _service.get_user(user_id=user_id, db=db)
    if request_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=settings.NO_USER_ERROR)

    return request_user


@router.delete("/{user_id}/")
async def delete_user(user_id: UUID, db: db_dependancy):
    request_user = await _service.get_user(user_id=user_id, db=db)
    if request_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=settings.NO_USER_ERROR)

    return await _service.delete_user(user=request_user, db=db)


@router.put("/{user_id}/", response_model=User)
async def edit_user(user_id: UUID, user_data: CreateUser, db: db_dependancy):
    request_user = await _service.get_user(user_id=user_id, db=db)
    if request_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=settings.NO_USER_ERROR)

    if user_data.phone_number:
        existing_user_with_phone = db.execute(
            select(user_model.User).where(
                user_model.User.phone_number == user_data.phone_number,
                user_model.User.id != user_id  # Exclude the current user being edited
            )
        )
        duplicate_user = existing_user_with_phone.scalar_one_or_none()

        if duplicate_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "status": "error",
                    "message": "Phone number already registered by another user."
                }
            )

    if user_data.email:
        existing_user_with_email = db.execute(
            select(user_model.User).where(
                user_model.User.email == user_data.email,
                user_model.User.id != user_id
            )
        )
        duplicate_user = existing_user_with_email.scalar_one_or_none()

        if duplicate_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "status": "error",
                    "message": "Email already registered by another user."
                }
            )

    return await _service.update_user(user=request_user, user_data=user_data, db=db)


@router.patch("/{user_id}/", response_model=User)
async def patch_user(user_id: UUID, user_patch: PatchUser, db: db_dependancy):
    request_user = await _service.get_user(user_id=user_id, db=db)
    if request_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=settings.NO_USER_ERROR)

    return await _service.patch_user(user=request_user, user_patch=user_patch, db=db)
