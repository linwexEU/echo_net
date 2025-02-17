from pydantic import BaseModel, Field 


class AddBookmarksToDb(BaseModel): 
    user_id: int = Field(...) 
    post_id: int = Field(...)


class BookmarksFilter(BaseModel): 
    user_id: int | None = None 
    post_id: int | None = None 


class BookmarksAddResponse(BaseModel): 
    bookmark_id: int = Field(...) 


class BookmarksDeleteResponse(BookmarksAddResponse): 
    pass
