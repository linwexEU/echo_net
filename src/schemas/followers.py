from pydantic import BaseModel, Field
from fastapi_cache.decorator import cache
from src.models.models import Followers 


class FollowerAddToDb(BaseModel): 
    follower_id: int = Field(...) 
    followed_id: int = Field(...)


class FollowedAddResponse(FollowerAddToDb): 
    pass 


class UsersData(BaseModel): 
    id: int = Field(...)
    username: str = Field(...)


class FollowerResponse(BaseModel): 
    total_count: int = Field(...) 
    users: list[UsersData]

    @staticmethod 
    @cache(expire=3)
    def from_orm(followers: list[Followers]) -> "FollowerResponse": 
        users_data = [] 
        for follower in followers: 
            users_data.append(
                UsersData(id=follower.followed_user.id, username=follower.followed_user.username)
            )
        return FollowerResponse(total_count=len(followers), users=users_data)
    

class FollowingResponse(FollowerResponse): 
    @staticmethod 
    @cache(expire=3)
    def from_orm(followers: list[Followers]) -> "FollowingResponse": 
        users_data = [] 
        for follower in followers: 
            users_data.append(
                UsersData(id=follower.follower_user.id, username=follower.follower_user.username)
            )
        return FollowingResponse(total_count=len(followers), users=users_data)


class FollowerFilters(BaseModel): 
    follower_id: int | None = None 
    followed_id: int | None = None 


class FollowerDeleteResponse(FollowerAddToDb): 
    pass 
