from pydantic import BaseModel, Field 


class LikedCommentsAddToDb(BaseModel): 
    user_id: int = Field(...) 
    comment_id: int = Field(...) 


class LikedCommentsFilters(BaseModel): 
    user_id: int | None = None 
    comment_id: int | None = None 
