from pydantic import BaseModel, Field 
from src.models.enums import NotificationStatus, NotificationsState


class AddNotificationsToDb(BaseModel): 
    user_id: int = Field(...) 
    status: NotificationStatus = Field(...) 
    message: str = Field(...)


class NotificationsFilters(BaseModel):
    id: int | None = None 
    user_id: int | None = None
    status: NotificationStatus | None = None 
    state: NotificationsState | None = None 


class GetNotifications(BaseModel):
    id: int = Field(...)
    user_id: int = Field(...)
    message: str = Field(...) 
    status: NotificationStatus = Field(...)
    state: NotificationsState = Field(...)
