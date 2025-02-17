from fastapi import APIRouter, Depends, HTTPException, status 
from src.schemas.notifications import GetNotifications, NotificationsFilters
from src.api.dependencies import notifications_service
from src.services.notifications import NotificationsService
from src.auth.dependencies import get_current_user
from src.models.models import Users 
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
import src.logger 
import logging
from fastapi_utils.cbv import cbv 


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@cbv(router) 
class NotificationsApi: 
    def __init__(self): 
        self.notifications_service: NotificationsService = notifications_service()

        self.logger = logging.getLogger(__name__) 
    
    @router.get("/", response_model=list[GetNotifications])
    async def get_notifications(self, current_user: Annotated[Users, Depends(get_current_user)]) -> list[GetNotifications]: 
        notifications = await self.notifications_service.get_by_filters(NotificationsFilters(user_id=current_user.id), one=False)
        return notifications

    @router.patch("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
    async def mark_as_read(self, notification_id: int, current_user: Annotated[Users, Depends(get_current_user)]):
        try:
            await self.notifications_service.change_state_to_read(notification_id)
            return "", 204 
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else:
                self.logger.error("Unknown error: %s"  % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 
