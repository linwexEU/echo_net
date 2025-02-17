from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status, Request
import jwt

from src.api.dependencies import users_service
from src.config import settings
from src.schemas.users import UsersFiltersSchema
from src.services.users import UsersService 

def get_token(request: Request) -> str: 
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication error. Try again!") 
    return token 


async def get_current_user(token: Annotated[str, Depends(get_token)], users_service: Annotated[UsersService, Depends(users_service)]):
    try: 
        payload: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.InvalidTokenError: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication error. Try again!") 

    # Check expire
    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.now(timezone.utc).timestamp()): 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication error. Try again!") 

    # Get user_id
    user_id: str = payload.get("sub")
    if not user_id: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication error. Try again!")  
    
    # Get user
    user = await users_service.get_by_filters(UsersFiltersSchema(id=int(user_id)))
    if not user: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication error. Try again!")   
    
    if user.report_count > 10: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have been blocked!")
    
    return user 
