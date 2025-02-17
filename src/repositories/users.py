from src.utils.repository import SQLAlchemyRepository 
from sqlalchemy import update 
from src.db.db import async_session_maker
from src.models.models import Users 


class UsersRepository(SQLAlchemyRepository): 
    model = Users 

    async def change_icon(self, user_id: int, icon: bytes) -> int: 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.id == user_id).values(icon=icon).returning(self.model.id) 
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar()
        
    async def increase_report_count(self, user_id: int) -> int: 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.id == user_id).values(report_count=self.model.report_count + 1).returning(self.model.id) 
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar()
