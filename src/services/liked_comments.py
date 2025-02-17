from src.schemas.liked_comments import LikedCommentsAddToDb, LikedCommentsFilters
from src.repositories.liked_comments import LikedCommentsRepository 


class LikedCommentsService: 
    def __init__(self, liked_comment_repo: LikedCommentsRepository): 
        self.liked_comment_repo: LikedCommentsRepository = liked_comment_repo() 

    async def add(self, data: LikedCommentsAddToDb) -> int: 
        data_to_dict = data.model_dump() 
        return await self.liked_comment_repo.add(data_to_dict) 
    
    async def get_by_filters(self, filters: LikedCommentsFilters): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.liked_comment_repo.get_by_filters(filters_to_dict)

    async def delete_liked_comment(self, user_id: int, comment_id: int) -> int: 
        return await self.liked_comment_repo.delete_liked_comment(user_id, comment_id)
