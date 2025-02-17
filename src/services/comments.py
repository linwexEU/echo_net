from src.schemas.comments import CommentAddToDb, CommentFilters
from src.repositories.comments import CommentsRepository 


class CommentsService: 
    def __init__(self, com_repo: CommentsRepository) -> None: 
        self.com_repo: CommentsRepository = com_repo() 

    async def add(self, data: CommentAddToDb) -> int: 
        data_to_dict = data.model_dump() 
        return await self.com_repo.add(data_to_dict)

    async def get_by_filters(self, filters: CommentFilters): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.com_repo.get_by_filters(filters_to_dict)
    
    async def delete_one(self, comment_id: int) -> int: 
        return await self.com_repo.delete_one(comment_id)
    
    async def like_comment(self, comment_id: int) -> int: 
        return await self.com_repo.like_comment(comment_id) 
    
    async def unlike_comment(self, comment_id: int) -> int: 
        return await self.com_repo.unlike_comment(comment_id) 
