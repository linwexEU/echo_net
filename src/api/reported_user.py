from fastapi import APIRouter, Depends, HTTPException, status 
from src.schemas.reported_user import ReportedUserAddToDb, ReportedUserFilters, ReportedUserResponse
from src.models.models import Users 
from src.auth.dependencies import get_current_user 
from typing import Annotated
from src.api.dependencies import reported_user_service, users_service
from src.services.users import UsersService
from src.services.reported_user import ReportedUserService 
import src.logger 
from sqlalchemy.exc import SQLAlchemyError
import logging 
from fastapi_utils.cbv import cbv


router = APIRouter(prefix="/report", tags=["Report User"])


@cbv(router) 
class ReportedUserApi: 
    def __init__(self): 
        self.reported_user_service: ReportedUserService = reported_user_service()
        self.users_service: UsersService = users_service() 

        self.logger = logging.getLogger(__name__) 

    @router.post("/users/{user_id}", response_model=ReportedUserResponse)
    async def report_user(self, user_id: int, current_user: Annotated[Users, Depends(get_current_user)]) -> ReportedUserResponse: 
        if user_id == current_user.id: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't report yourself!")
        
        report = await self.reported_user_service.get_by_filters(ReportedUserFilters(reporter_id=current_user.id, user_id=user_id)) 
        if report: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reported this user!")
        
        try: 
            report_id = await self.reported_user_service.add(ReportedUserAddToDb(reporter_id=current_user.id, user_id=user_id))
            await self.users_service.increase_report_count(user_id)
            return ReportedUserResponse(report_id=report_id)
        except Exception as ex: 
            if isinstance(ex, SQLAlchemyError): 
                self.logger.error("Db error: %s" % ex) 
            else: 
                self.logger.error("Unknown error: %s" % ex) 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 
