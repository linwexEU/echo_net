from src.models.models import Bookmarks 
from src.db.db import async_session_maker 
from sqlalchemy import delete
from src.utils.repository import SQLAlchemyRepository 


class BookmarksRepository(SQLAlchemyRepository): 
    model = Bookmarks 

    async def delete_bookmark(self, post_id: int, user_id: int) -> int: 
        async with async_session_maker() as session: 
            query = delete(self.model).where(self.model.post_id == post_id, self.model.user_id == user_id).returning(self.model.id) 
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar() 
