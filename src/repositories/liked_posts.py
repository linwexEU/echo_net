from src.utils.repository import SQLAlchemyRepository 
from src.db.db import async_session_maker
from sqlalchemy import delete
from src.models.models import LikedPosts 


class LikedPostsRepository(SQLAlchemyRepository): 
    model = LikedPosts 

    async def delete_like(self, user_id: int, post_id: int) -> int: 
        async with async_session_maker() as session: 
            query = delete(self.model).where(self.model.user_id == user_id, self.model.post_id == post_id).returning(self.model.id) 
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar() 
