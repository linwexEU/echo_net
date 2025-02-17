from src.schemas.bookmarks import AddBookmarksToDb, BookmarksFilter
from src.repositories.bookmarks import BookmarksRepository 


class BookmarksService: 
    def __init__(self, book_repo: BookmarksRepository): 
        self.book_repo: BookmarksRepository = book_repo() 

    async def add(self, data: AddBookmarksToDb) -> int: 
        data_to_dict = data.model_dump() 
        return await self.book_repo.add(data_to_dict)
    
    async def get_by_filters(self, filters: BookmarksFilter): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.book_repo.get_by_filters(filters_to_dict)
    
    async def delete_bookmark(self, post_id: int, user_id: int) -> int: 
        return await self.book_repo.delete_bookmark(post_id, user_id)
