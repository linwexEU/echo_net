from pydantic import BaseModel, Field 


class LikedPostsAddToDb(BaseModel): 
    user_id: int = Field(...) 
    post_id: int = Field(...) 


class LikedPostsFilters(LikedPostsAddToDb): 
    pass 
