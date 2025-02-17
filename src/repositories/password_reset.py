from src.models.models import PasswordReset 
from sqlalchemy import update, select
from src.db.db import async_session_maker
from datetime import datetime
from src.utils.repository import SQLAlchemyRepository 


class PasswordResetRepository(SQLAlchemyRepository): 
    model = PasswordReset 

    async def set_applied_date_time(self, user_id: int, applied_date_time: datetime) -> None: 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.user_id == user_id).values(applied_date_time=applied_date_time)
            await session.execute(query) 
            await session.commit() 

    async def get_last_reset_request(self, user_id, un_used=True): 
        async with async_session_maker() as session: 
            if un_used:
                query = select(self.model).where(self.model.user_id == user_id, self.model.applied_date_time.is_(None)).order_by(self.model.create_date_time.desc())
            else: 
                query = select(self.model).where(self.model.user_id == user_id).order_by(self.model.create_date_time.desc())
            query_result = await session.execute(query) 

            result = query_result.scalars().all()

            if result:
                return result[0] 
