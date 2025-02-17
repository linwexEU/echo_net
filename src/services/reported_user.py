from src.schemas.reported_user import ReportedUserAddToDb, ReportedUserFilters
from src.repositories.reported_user import ReportedUserRepository 


class ReportedUserService: 
    def __init__(self, report_user_repo: ReportedUserRepository): 
        self.report_user_repo: ReportedUserRepository = report_user_repo() 

    async def add(self, data: ReportedUserAddToDb) -> int: 
        data_to_dict = data.model_dump() 
        return await self.report_user_repo.add(data_to_dict)

    async def get_by_filters(self, filters: ReportedUserFilters): 
        filters_to_dict = filters.model_dump(exclude_none=True) 
        return await self.report_user_repo.get_by_filters(filters_to_dict)
