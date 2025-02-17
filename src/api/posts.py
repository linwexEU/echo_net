from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, Form
from fastapi.responses import StreamingResponse
from src.schemas.comments import CommentAddToDb, CommentFilters
from src.schemas.liked_posts import LikedPostsAddToDb, LikedPostsFilters
from src.schemas.posts import PostCreateResponseSchema, PostsFilters, GetPosts, DeletePostResponse, PostUpdateSchema, PostsSearch
from src.auth.dependencies import get_current_user
from fastapi_utils.cbv import cbv
from src.services.posts import PostsService 
from src.services.liked_posts import LikedPostsService
from src.services.followers import FollowersService
from src.services.comments import CommentsService
from src.api.dependencies import posts_service, liked_post_service, users_service, comments_service, followers_service
from src.services.users import UsersService
from src.models.models import Users
from src.utils.notifications import SendNotifications
from fastapi_cache.decorator import cache
import src.logger 
import magic 
import io
import logging 
from src.config import settings
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated


router = APIRouter(prefix="/posts", tags=["Posts"])
extensions = ["mp4", "mp3", "jpg", "jpeg", "webm", "png"]


@cbv(router) 
class PostsApi: 
    def __init__(self): 
        self.users_service: UsersService = users_service()
        self.posts_service: PostsService = posts_service() 
        self.liked_post_service: LikedPostsService = liked_post_service()
        self.comments_service: CommentsService = comments_service()
        self.followers_service: FollowersService = followers_service()

        self.logger = logging.getLogger(__name__)

    @router.post("/", response_model=list[GetPosts])
    async def get_posts(self, search: PostsSearch | None = None) -> list[GetPosts]: 
        
        # Get all posts
        @cache(expire=3)
        async def get_all_posts(): 
            return await self.posts_service.get_posts_with_comments(search)
        
        posts = await get_all_posts()
        return posts 
    
    @router.post("/user/{user_id}", response_model=list[GetPosts])
    async def get_user_posts(self, user_id: int, search: PostsSearch | None = None) -> list[GetPosts]: 

        # Get user's posts
        @cache(expire=3)
        async def get_user_posts(user_id: int): 
            return await self.posts_service.get_user_posts_with_comments(user_id, search)
        
        posts =  await get_user_posts(user_id)
        return posts 
    
    @router.post("/feed", response_model=list[GetPosts]) 
    async def get_post_from_followinf(self, current_user: Annotated[Users, Depends(get_current_user)]) -> list[GetPosts]: 
        following_ids = [item.follower_id for item in await self.followers_service.get_user_following(current_user.id)]

        @cache(expire=3) 
        async def get_posts(): 
            return await self.posts_service.get_posts_from_following_user(following_ids)
        
        posts = await get_posts() 
        return posts 

    @router.post("/create", response_model=PostCreateResponseSchema)
    async def create_post(self, media: UploadFile, title: Annotated[str, Form()], current_user: Annotated[Users, Depends(get_current_user)], description: Annotated[str, Form()] = None) -> PostCreateResponseSchema:
        # Check media
        self.check_media(media) 
        
        try: 
            post_id = await self.posts_service.add({"user_id": current_user.id, "title": title, "description": description, "file": media.file.read()}) 
            
            # Send notifications to followers
            follower_ids = [item.followed_id for item in await self.followers_service.get_user_followers(current_user.id)]
            await SendNotifications.send_new_post_notification(follower_ids, current_user.username)

            return PostCreateResponseSchema(post_id=post_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    @router.delete("/{post_id}", response_model=DeletePostResponse)
    async def delete_post(self, post_id: int, current_user: Annotated[Users, Depends(get_current_user)]) -> DeletePostResponse:
        # Check post access
        await self.ensure_post_access(post_id, current_user)

        # Delete Post 
        try:
            await self.posts_service.delete_one(post_id)
            return DeletePostResponse(post_id=post_id) 
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
    @router.get("/media/{post_id}")
    async def load_post_media(self, post_id: int):
        # Get post
        post = await self.posts_service.get_by_filters(PostsFilters(id=post_id))

        if not post: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post(Id={post_id}) was not found")
        
        # Get type of media
        mime = magic.Magic(mime=True) 
        mime_type = mime.from_buffer(post.file) 

        return StreamingResponse(io.BytesIO(post.file), media_type=mime_type)
    
    @router.put("/{post_id}/edit", status_code=status.HTTP_204_NO_CONTENT)
    async def edit_post(self, post_id: int, data: PostUpdateSchema, current_user: Annotated[Users, Depends(get_current_user)]): 
        # Check post access
        await self.ensure_post_access(post_id, current_user)
        
        try:
            await self.posts_service.update_one(post_id, data)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex)
            else: 
                self.logger.error("Unknown error: %s" % ex)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
        return "", 204  
    
    @router.patch("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
    async def like_post(self, post_id: int, current_user: Annotated[Users, Depends(get_current_user)]): 
        # Check that post exists 
        post = await self.posts_service.get_by_filters(PostsFilters(id=post_id))
        if not post: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post(Id={post_id}) wasn't found")

        # Get LikedPost
        liked_post = await self.liked_post_service.get_by_filters(LikedPostsFilters(user_id=current_user.id, post_id=post_id))
        if liked_post: 
            return "", 204 
        
        # Like post
        try: 
            await self.posts_service.like_post(post_id) 
            await self.liked_post_service.add(LikedPostsAddToDb(user_id=current_user.id, post_id=post_id))

            # Send notifications to post creator
            if post.user_id != current_user.id:
                await SendNotifications.send_liked_post_notification(current_user.username, post.user_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex)
            else: 
                self.logger.error("Unknown error: %s" % ex)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
        return "", 204
    
    @router.patch("/{post_id}/unlike", status_code=status.HTTP_204_NO_CONTENT)
    async def unlike_post(self, post_id: int, current_user: Annotated[Users, Depends(get_current_user)]): 
        # Get LikedPost
        liked_post = await self.liked_post_service.get_by_filters(LikedPostsFilters(user_id=current_user.id, post_id=post_id)) 
        if not liked_post: 
            return "", 204 
        
        # Unlike post
        try: 
            await self.posts_service.unlike_post(post_id) 
            await self.liked_post_service.delete_like(current_user.id, post_id) 
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex)
            else: 
                self.logger.error("Unknown error: %s" % ex)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 

        return "", 204
    
    @router.patch("/{post_id}/comment", status_code=status.HTTP_204_NO_CONTENT)
    async def add_comment(self, post_id: int, comment: str, current_user: Annotated[Users, Depends(get_current_user)]):
        # Check that post exists 
        post = await self.posts_service.get_by_filters(PostsFilters(id=post_id))
        if not post: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post(Id={post_id}) wasn't found")
        
        try:
            await self.comments_service.add(CommentAddToDb(user_id=current_user.id, post_id=post_id, text=comment))

            # Send notifications to post creator
            if post.user_id != current_user.id:
                await SendNotifications.send_comment_added_notification(current_user.username, post.user_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
        return "", 204
    
    @router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_comment(self, comment_id: int, current_user: Annotated[Users, Depends(get_current_user)]):
        # Check that comment exists 
        comment = await self.comments_service.get_by_filters(CommentFilters(id=comment_id))
        if not comment: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) 
        
        # Check that user can delete this comment
        if comment.user_id != current_user.id: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You can't delete Comment(Id={comment_id})")
        
        try:
            await self.comments_service.delete_one(comment_id)
            return "", 204 
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex)
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod 
    def check_media(media: UploadFile): 
        if media.filename.split(".")[-1] not in extensions: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="You must choose an image with one of the following extensions: JPG, JPEG, WEBM, PNG, MP4, MP3")
        
        if media.size > settings.MAX_MEDIA_SIZE: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Maximum size of media is 5MB")
    
    async def ensure_post_access(self, post_id, current_user):
        # Check that post exists 
        post = await self.posts_service.get_by_filters(PostsFilters(id=post_id))
        if not post: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post(Id={post_id}) wasn't found")
        
        # Check that you can act with post(Id=post_id)
        if post.user_id != current_user.id: 
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can act only with your posts")
