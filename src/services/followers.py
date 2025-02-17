from src.schemas.followers import FollowerAddToDb, FollowerFilters
from src.repositories.followers import FollowersRepository 


class FollowersService: 
    def __init__(self, followers_repo: FollowersRepository): 
        self.followers_repo: FollowersRepository = followers_repo() 

    async def add(self, data: FollowerAddToDb) -> int: 
        data_to_dict = data.model_dump() 
        return await self.followers_repo.add(data_to_dict)
    
    async def get_by_filters(self, filters: FollowerFilters): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.followers_repo.get_by_filters(filters_to_dict)
    
    async def delete_one(self, follow_id: int) -> None: 
        return await self.followers_repo.delete_one(follow_id)
    
    async def get_user_followers(self, user_id: int): 
        return await self.followers_repo.get_user_followers(user_id)
    
    async def get_user_following(self, user_id: int): 
        return await self.followers_repo.get_user_following(user_id) 
