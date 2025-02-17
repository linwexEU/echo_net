from src.schemas.notifications import AddNotificationsToDb, NotificationsFilters
from src.repositories.notifications import NotificationsRepository 


class NotificationsService: 
    def __init__(self, not_repo: NotificationsRepository): 
        self.not_repo: NotificationsRepository = not_repo() 

    async def add(self, data: AddNotificationsToDb) -> int: 
        data_to_dict = data.model_dump() 
        return await self.not_repo.add(data_to_dict)
    
    async def get_by_filters(self, filters: NotificationsFilters, one=True): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.not_repo.get_by_filters(filters_to_dict, one)

    async def change_state_to_read(self, notification_id: int) -> int: 
        return await self.not_repo.change_state_to_read(notification_id)
        