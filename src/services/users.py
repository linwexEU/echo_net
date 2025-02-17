from src.schemas.users import UsersAddSchema, UsersFiltersSchema, UsersUpdateSchema
from src.repositories.users import UsersRepository 


class UsersService: 
    def __init__(self, user_repo: UsersRepository): 
        self.user_repo: UsersRepository = user_repo() 

    async def add(self, data: UsersAddSchema) -> int:
        data_to_dict = data.model_dump() 
        return await self.user_repo.add(data_to_dict) 

    async def get_all(self): 
        return await self.user_repo.get_all()

    async def get_by_filters(self, filters: UsersFiltersSchema, one: bool = True): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.user_repo.get_by_filters(filters_to_dict, one)

    async def update_one(self, user_id: int, data: UsersUpdateSchema) -> None:
        data_to_dict = data.model_dump(exclude_none=True) 
        await self.user_repo.update_one(user_id, data_to_dict)

    async def delete_one(self, user_id: int) -> None: 
        await self.user_repo.delete_one(user_id) 

    async def change_icon(self, user_id: int, icon: bytes) -> int: 
        return await self.user_repo.change_icon(user_id, icon)

    async def increase_report_count(self, user_id: int) -> int: 
        return await self.user_repo.increase_report_count(user_id) 
