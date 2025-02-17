from src.utils.repository import SQLAlchemyRepository 
from src.db.db import async_session_maker 
from sqlalchemy import update, select
from sqlalchemy.orm import selectinload
from src.models.models import Bookmarks, Posts


class PostsRepository(SQLAlchemyRepository): 
    model = Posts 
    
    async def like_post(self, post_id: int): 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.id == post_id).values(likes=self.model.likes + 1).returning(self.model.id)
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar() 

    async def unlike_post(self, post_id: int): 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.id == post_id).values(likes=self.model.likes - 1).returning(self.model.id)
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar()
        
    async def get_posts_with_comments(self, search: dict| None = None): 
        async with async_session_maker() as session: 
            query = select(self.model).options(selectinload(self.model.comments))
            if search["search"]:
                query = query.where(self.model.title.icontains(search["search"]))
            if search["offset"] is not None and search["limit"] is not None: 
                query = query.offset(search["offset"]).limit(search["limit"])

            result = await session.execute(query) 

            return self.generate_posts_model(result.scalars().all())
        
    async def get_user_posts_with_comments(self, user_id: int, search: dict| None = None): 
        async with async_session_maker() as session: 
            query = select(self.model).where(self.model.user_id == user_id).options(selectinload(self.model.comments))
            if search["search"]:
                query = query.where(self.model.title.icontains(search["search"]))
            if search["offset"] is not None and search["limit"] is not None: 
                query = query.offset(search["offset"]).limit(search["limit"])
                
            result = await session.execute(query) 

            return self.generate_posts_model(result.scalars().all())
        
    async def get_posts_with_bookmark(self, user_id: int): 
        async with async_session_maker() as session: 
            query = select(self.model).join(Bookmarks).options(selectinload(self.model.comments)).where(Bookmarks.user_id == user_id)
            result = await session.execute(query) 

            return self.generate_posts_model(result.scalars().all())
        
    async def get_posts_from_following_user(self, following_ids: list[int]): 
        async with async_session_maker() as session: 
            query = select(self.model).where(self.model.user_id.in_(following_ids)).options(selectinload(self.model.comments))
            result = await session.execute(query) 

            return self.generate_posts_model(result.scalars().all()) 

    @staticmethod 
    def generate_posts_model(posts_db) -> list: 
        posts = []
        for post in posts_db: 
            post_data = {} 

            post_data["id"] = post.id 
            post_data["title"] = post.title 
            post_data["description"] = post.description 
            post_data["likes"] = post.likes 

            comments = []
            for comment in post.comments: 
                comment_data = {} 

                comment_data["id"] = comment.id 
                comment_data["post_id"] = comment.post_id 
                comment_data["user_id"] = comment.user_id 
                comment_data["text"] = comment.text 
                comment_data["likes"] = comment.likes

                comments.append(comment_data)

            post_data["comments"] = comments
            posts.append(post_data)

        return posts
