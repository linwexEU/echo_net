from pydantic import BaseModel, Field 


class CommentAddToDb(BaseModel): 
    user_id: int = Field(...) 
    post_id: int = Field(...) 
    text: str = Field(...) 


class CommentFilters(BaseModel): 
    id: int | None = None
    user_id: int | None = None 
    post_id: int | None = None 
