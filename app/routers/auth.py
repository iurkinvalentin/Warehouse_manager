from typing import List
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.data.database import get_db
from app.schemas.users import (
    Token, UserCreate, UserInDB, UserResponse, UserUpdate
    )
from app.services import user_service


router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = user_service.authenticate_user(
        db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=user_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserResponse = Depends(user_service.get_current_user),
):
    return current_user


@router.get("/users/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(user_service.get_current_user),
):
    return user_service.get_all_users(skip, limit, db)


@router.post("/register/", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    return user_service.register_handler(user_data, db)


@router.patch("/users/{user_id}")
def patch_user(user_id: int, user_data: UserUpdate,
               db: Session = Depends(get_db),
               current_user: UserInDB = Depends(
                   user_service.get_current_user)):
    return user_service.update_user_handler(user_id, user_data, db)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(user_service.get_current_user),
):
    if not current_user.id or current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя удалить другого пользователя",
        )
    return user_service.delete_user_handler(user_id, db)
