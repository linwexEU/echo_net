from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status

from src.api.dependencies import users_service 
from src.config import settings 
from src.schemas.users import UsersFiltersSchema
from src.services.users import UsersService 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(plain_password: str) -> str: 
    return pwd_context.hash(plain_password) 


def verify_password(plain_password: str, hashed_password: str) -> bool: 
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict): 
    to_encode = data.copy() 
    to_encode.update({"exp": datetime.now(timezone.utc) + timedelta(seconds=settings.TOKEN_EXPIRE)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt 


async def authenticate_user(email: str, password: str, users_service: UsersService = users_service()): 
    user = await users_service.get_by_filters(UsersFiltersSchema(email=email))

    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Can't find User(Email={email})")
    
    if not verify_password(password, user.hashed_password): 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    return user 
