from pydantic import BaseModel, Field


class PostsFilters(BaseModel): 
    id: int | None = None 
    user_id: int | None = None 


class PostUpdateSchema(BaseModel): 
    title: str | None = None 
    description: str | None = None


class CommentData(BaseModel): 
    id: int = Field(...)
    user_id: int = Field(...)
    text: str = Field(...)
    likes: int = Field(...)


class GetPosts(BaseModel):
    title: str 
    description: str | None = None
    likes: int 
    comments: list[CommentData] | None = [] 


class PostCreateSchema(BaseModel): 
    title: str = Field(...)
    description: str | None = None


class PostCreateResponseSchema(BaseModel): 
    post_id: int = Field(...) 


class DeletePostResponse(PostCreateResponseSchema): 
    pass 


class PostsSearch(BaseModel): 
    search: str | None = None 
    offset: int | None = None 
    limit: int | None = None
