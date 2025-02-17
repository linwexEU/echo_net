from src.schemas.posts import PostsFilters, PostUpdateSchema, PostsSearch
from src.repositories.posts import PostsRepository 


class PostsService: 
    def __init__(self, posts_repo: PostsRepository): 
        self.posts_repo: PostsRepository = posts_repo() 

    async def add(self, data: dict) -> int: 
        return await self.posts_repo.add(data)
    
    async def get_all(self): 
        return await self.posts_repo.get_all() 
    
    async def get_by_filters(self, filters: PostsFilters, one=True): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.posts_repo.get_by_filters(filters_to_dict, one) 
    
    async def update_one(self, post_id: int, data: PostUpdateSchema) -> None: 
        data_to_dict = data.model_dump() 
        await self.posts_repo.update_one(post_id, data_to_dict) 

    async def delete_one(self, post_id: int) -> None: 
        await self.posts_repo.delete_one(post_id)

    async def like_post(self, post_id: int) -> int: 
        return await self.posts_repo.like_post(post_id) 
    
    async def unlike_post(self, post_id: int) -> int: 
        return await self.posts_repo.unlike_post(post_id)

    async def get_posts_with_comments(self, search: PostsSearch | None = None):
        search_to_data = None  
        if search: 
            search_to_data = search.model_dump()
        return await self.posts_repo.get_posts_with_comments(search_to_data)

    async def get_user_posts_with_comments(self, user_id: int, search: PostsSearch | None = None):
        search_to_data = None  
        if search: 
            search_to_data = search.model_dump() 
        return await self.posts_repo.get_user_posts_with_comments(user_id, search_to_data)

    async def get_posts_with_bookmark(self, user_id: int): 
        return await self.posts_repo.get_posts_with_bookmark(user_id) 

    async def get_posts_from_following_user(self, following_ids: list[int]): 
        return await self.posts_repo.get_posts_from_following_user(following_ids)
