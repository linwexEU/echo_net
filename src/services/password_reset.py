from src.schemas.password_reset import PasswordResetAddToDb, PasswordResetFilters
from src.repositories.password_reset import PasswordResetRepository
from datetime import datetime  


class PasswordResetService: 
    def __init__(self, pass_repo: PasswordResetRepository): 
        self.pass_repo: PasswordResetRepository = pass_repo()

    async def add(self, data: PasswordResetAddToDb) -> int: 
        data_to_dict = data.model_dump() 
        return await self.pass_repo.add(data_to_dict)
    
    async def get_by_filters(self, filters: PasswordResetFilters): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.pass_repo.get_by_filters(filters_to_dict)

    async def set_applied_date_time(self, user_id: int, applied_date_time: datetime) -> None: 
        await self.pass_repo.set_applied_date_time(user_id, applied_date_time)

    async def get_last_reset_request(self, user_id: int, un_used=True): 
        return await self.pass_repo.get_last_reset_request(user_id, un_used)
