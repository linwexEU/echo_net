from src.models.enums import NotificationsState
from src.utils.repository import SQLAlchemyRepository
from src.db.db import async_session_maker 
from datetime import datetime, timezone
from sqlalchemy import update
from src.models.models import Notifications


class NotificationsRepository(SQLAlchemyRepository): 
    model = Notifications 

    async def change_state_to_read(self, notification_id: int) -> int: 
        async with async_session_maker() as session: 
            query = update(self.model).where(self.model.id == notification_id).values(state=NotificationsState.Read, delete_date_time=datetime.now(timezone.utc)).returning(self.model.id)
            result = await session.execute(query) 

            await session.commit() 
            return result 
