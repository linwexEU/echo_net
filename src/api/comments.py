from fastapi import APIRouter, Depends, HTTPException, status
from src.schemas.comments import CommentFilters
from src.schemas.liked_comments import LikedCommentsAddToDb, LikedCommentsFilters
from src.api.dependencies import liked_comments_service, comments_service
from src.models.models import Users 
from src.auth.dependencies import get_current_user
from src.services.liked_comments import LikedCommentsService
from src.services.comments import CommentsService
from src.utils.notifications import SendNotifications
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
import src.logger 
import logging
from fastapi_utils.cbv import cbv 


router = APIRouter(prefix="/comments", tags=["Comments"])


@cbv(router) 
class CommentsApi: 
    def __init__(self): 
        self.liked_comments_service: LikedCommentsService = liked_comments_service()
        self.comments_service: CommentsService = comments_service()

        self.logger = logging.getLogger(__name__) 

    @router.patch("/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
    async def liked_comment(self, comment_id: int, current_user: Annotated[Users, Depends(get_current_user)]): 
        # Check that comment is exists
        comment = await self.comments_service.get_by_filters(CommentFilters(id=comment_id))
        if not comment: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment(Id={comment_id}) wasn't found")
        
        # Check if comment has already liked 
        liked_comment = await self.liked_comments_service.get_by_filters(LikedCommentsFilters(user_id=current_user.id, comment_id=comment_id))
        if liked_comment: 
            return "", 204

        try: 
            await self.comments_service.like_comment(comment_id) 
            await self.liked_comments_service.add(LikedCommentsAddToDb(user_id=current_user.id, comment_id=comment_id))

            # Send notification to comment creator 
            if comment.user_id != current_user.id:
                await SendNotifications.send_comment_liked_notification(current_user.username, comment.user_id)
            
            return "", 204 
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @router.patch("/{comment_id}/unlike", status_code=status.HTTP_204_NO_CONTENT)
    async def unliked_comment(self, comment_id: int, current_user: Annotated[Users, Depends(get_current_user)]): 
        # Check if comment has already liked 
        liked_comment = await self.liked_comments_service.get_by_filters(LikedCommentsFilters(user_id=current_user.id, comment_id=comment_id))
        if not liked_comment: 
            return "", 204
        
        try: 
            await self.comments_service.unlike_comment(comment_id)
            await self.liked_comments_service.delete_liked_comment(current_user.id, comment_id)
            return "", 204
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 
