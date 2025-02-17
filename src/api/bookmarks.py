from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi_utils.cbv import cbv
from src.schemas.posts import GetPosts
from src.schemas.bookmarks import AddBookmarksToDb, BookmarksAddResponse, BookmarksDeleteResponse, BookmarksFilter
from src.api.dependencies import bookmarks_service, posts_service 
from src.services.posts import PostsService
from src.services.bookmarks import BookmarksService
from sqlalchemy.exc import SQLAlchemyError
from src.models.models import Users 
from src.auth.dependencies import get_current_user
from fastapi_cache.decorator import cache
from typing import Annotated 
import src.logger 
import logging


router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@cbv(router) 
class BookmarksApi: 
    def __init__(self): 
        self.bookmarks_service: BookmarksService = bookmarks_service()
        self.posts_service: PostsService = posts_service()

        self.logger = logging.getLogger(__name__)

    @router.get("/", response_model=list[GetPosts])
    async def get_bookmarks(self, current_user: Annotated[Users, Depends(get_current_user)]) -> list[GetPosts]:
        
        @cache(expire=3)
        async def get_posts_bookmarks(): 
            return  await self.posts_service.get_posts_with_bookmark(current_user.id)
        
        posts = await get_posts_bookmarks() 
        return posts

    @router.post("/add/{post_id}", response_model=BookmarksAddResponse)
    async def add_bookmarks(self, post_id: int, current_user: Annotated[Users, Depends(get_current_user)]) -> BookmarksAddResponse: 
        bookmark = await self.bookmarks_service.get_by_filters(BookmarksFilter(post_id=post_id, user_id=current_user.id))
        if bookmark: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already added this post to bookmark")
        
        try:
            bookmark_id = await self.bookmarks_service.add(AddBookmarksToDb(post_id=post_id, user_id=current_user.id)) 
            return BookmarksAddResponse(bookmark_id=bookmark_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @router.delete("/remove/{post_id}", response_model=BookmarksDeleteResponse)
    async def remove_bookmarks(self, post_id: int, current_user: Annotated[Users, Depends(get_current_user)]) -> BookmarksDeleteResponse: 
        bookmark = await self.bookmarks_service.get_by_filters(BookmarksFilter(post_id=post_id, user_id=current_user.id))
        if not bookmark: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark wasn't found")
        
        try: 
            bookmark_id = await self.bookmarks_service.delete_bookmark(post_id, current_user.id)
            return BookmarksDeleteResponse(bookmark_id=bookmark_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
