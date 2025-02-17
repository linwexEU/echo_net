from src.utils.repository import SQLAlchemyRepository 
from src.db.db import async_session_maker
from src.models.models import IpDefender
from datetime import datetime
from sqlalchemy import update

class IpDefenderRepository(SQLAlchemyRepository):
    model = IpDefender 

    async def decrease_attempt(self, ip: str) -> int: 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.ip == ip).values(attempt=self.model.attempt - 1).returning(self.model.id) 
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar()

    async def set_applied_date_time(self, ip: str, date: datetime | None = None):
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.ip == ip).values(applied_date_time=date).returning(self.model.id) 
            result = await session.execute(query) 
            
            await session.commit() 

            return result.scalar()

    async def fill_attempt(self, ip: str): 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.ip == ip).values(attempt=2).returning(self.model.id) 
            result = await session.execute(query) 

            await session.commit() 

            return result.scalar()
        