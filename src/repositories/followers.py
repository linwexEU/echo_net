from src.models.models import Followers 
from src.db.db import async_session_maker 
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.utils.repository import SQLAlchemyRepository 


class FollowersRepository(SQLAlchemyRepository): 
    model = Followers 
    
    async def get_user_followers(self, user_id: int): 
        async with async_session_maker() as session: 
            query = select(self.model).where(self.model.follower_id == user_id).options(
                selectinload(self.model.followed_user)
            )
            result = await session.execute(query) 
            return result.scalars().all()  

    async def get_user_following(self, user_id: int):
        async with async_session_maker() as session: 
            query = select(self.model).where(self.model.followed_id == user_id).options(
                selectinload(self.model.follower_user)
            )
            result = await session.execute(query) 
            return result.scalars().all() 
