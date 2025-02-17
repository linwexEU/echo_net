from fastapi import APIRouter, Depends, HTTPException, status 
from src.schemas.followers import FollowedAddResponse, FollowerAddToDb, FollowerDeleteResponse, FollowerFilters, FollowerResponse, FollowingResponse
from src.auth.dependencies import get_current_user 
from src.models.models import Users
from src.api.dependencies import followers_service 
from sqlalchemy.exc import SQLAlchemyError
from src.services.followers import FollowersService 
from src.utils.notifications import SendNotifications
from typing import Annotated 
import logging 
import src.logger
from fastapi_utils.cbv import cbv 


router = APIRouter(prefix="/followers", tags=["Followers & Following"])


@cbv(router) 
class FollowersApi: 
    def __init__(self): 
        self.followers_service: FollowersService = followers_service()

        self.logger = logging.getLogger(__name__)

    @router.get("/followed", response_model=FollowerResponse)
    async def get_followers(self, current_user: Annotated[Users, Depends(get_current_user)]) -> FollowerResponse: 
        try:
            followers = await self.followers_service.get_user_followers(current_user.id) 
            return await FollowerResponse.from_orm(followers)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @router.get("/following", response_model=FollowingResponse)
    async def get_following(self, current_user: Annotated[Users, Depends(get_current_user)]) -> FollowingResponse:
        try: 
            following = await self.followers_service.get_user_following(current_user.id)
            return await FollowingResponse.from_orm(following)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    @router.post("/followed/{user_id}", response_model=FollowedAddResponse)
    async def follow_to_user(self, user_id: int, current_user: Annotated[Users, Depends(get_current_user)]) -> FollowedAddResponse: 
        if user_id == current_user.id: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't follow yourself")
        
        follow = await self.followers_service.get_by_filters(FollowerFilters(follower_id=user_id, followed_id=current_user.id))
        if follow: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already followed on this user")
        
        try:
            await self.followers_service.add(FollowerAddToDb(follower_id=user_id, followed_id=current_user.id))

            # Send notification to followed 
            await SendNotifications.send_following_notification(current_user.username, user_id)
            
            return FollowerAddToDb(follower_id=current_user.id, followed_id=user_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    @router.delete("/followed/{user_id}", response_model=FollowerDeleteResponse)
    async def unfollow_from_user(self, user_id: int, current_user: Annotated[Users, Depends(get_current_user)]) -> FollowerDeleteResponse: 
        if user_id == current_user.id: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't")    
        
        follow = await self.followers_service.get_by_filters(FollowerFilters(follower_id=user_id, followed_id=current_user.id))
        if not follow: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't unfollow from this user")
        
        try: 
            await self.followers_service.delete_one(follow.id)
            return FollowerDeleteResponse(follower_id=current_user.id, followed_id=user_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
