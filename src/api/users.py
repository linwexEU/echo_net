from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from src.schemas.users import AddBioSchema, UsersIconResponseSchema, UsersInfoSchema, UsersUpdateSchema
from src.services.users import UsersService 
from src.api.dependencies import users_service
from typing import Annotated 
from src.models.models import Users 
from src.auth.dependencies import get_current_user
from fastapi.responses import StreamingResponse
import io 
import src.logger 
from src.config import settings
from sqlalchemy.exc import SQLAlchemyError
import logging
from fastapi_utils.cbv import cbv

router = APIRouter(prefix="/users", tags=["Users Account"])
extensions = ["jpg", "jpeg", "webp", "png"]


@cbv(router)
class UsersApi: 
    def __init__(self): 
        self.users_service: UsersService = users_service() 

        self.logger = logging.getLogger(__name__) 

    @router.get("/info", response_model=UsersInfoSchema)
    async def get_user_info(self, current_user: Annotated[Users, Depends(get_current_user)]) -> UsersInfoSchema: 
        return current_user
    
    @router.get("/icon")
    async def load_user_icon(self, current_user: Annotated[Users, Depends(get_current_user)]): 
        return StreamingResponse(io.BytesIO(current_user.icon), media_type="image/jpg")

    @router.post("/icon", response_model=UsersIconResponseSchema)
    async def change_user_icon(self, icon: UploadFile, current_user: Annotated[Users, Depends(get_current_user)]) -> UsersIconResponseSchema: 
        # Check icon 
        self.check_icon(icon)
        
        user_id = await self.users_service.change_icon(current_user.id, icon.file.read()) 
        return UsersIconResponseSchema(user_id=user_id)
    
    @router.patch("/bio", status_code=status.HTTP_204_NO_CONTENT)
    async def add_bio(self, data: AddBioSchema, current_user: Annotated[Users, Depends(get_current_user)]):
        try: 
            await self.users_service.update_one(current_user.id, UsersUpdateSchema(bio=data.bio)) 
            return "", 204 
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod 
    def check_icon(icon: UploadFile): 
        if icon.filename.split(".")[-1] not in extensions: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="You must choose an image with one of the following extensions: JPG, JPEG, WEBP, PNG")
        
        if icon.size > settings.MAX_ICON_SIZE: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Maximum size of file is 1MB")
        