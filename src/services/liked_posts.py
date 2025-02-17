from src.schemas.liked_posts import LikedPostsFilters, LikedPostsAddToDb
from src.repositories.liked_posts import LikedPostsRepository 


class LikedPostsService: 
    def __init__(self, liked_posts_repo: LikedPostsRepository): 
        self.liked_posts_repo: LikedPostsRepository = liked_posts_repo()

    async def get_by_filters(self, filters: LikedPostsFilters, one=True): 
        filters_to_dict = filters.model_dump() 
        return await self.liked_posts_repo.get_by_filters(filters_to_dict, one) 
    
    async def add(self, data: LikedPostsAddToDb): 
        data_to_dict = data.model_dump() 
        return await self.liked_posts_repo.add(data_to_dict) 
    
    async def delete_like(self, user_id: int, post_id: int) -> int: 
        return await self.liked_posts_repo.delete_like(user_id, post_id)
