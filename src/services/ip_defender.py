from src.schemas.ip_defender import IpDefenderAddToDbSchema, IpDefenderFiltersSchema
from src.repositories.ip_defender import IpDefenderRepository 
from datetime import datetime


class IpDefenderService: 
    def __init__(self, ip_def_repo: IpDefenderRepository): 
        self.ip_def_repo: IpDefenderRepository = ip_def_repo() 

    async def add(self, data: IpDefenderAddToDbSchema) -> int: 
        data_to_dict = data.model_dump() 
        return await self.ip_def_repo.add(data_to_dict)

    async def get_by_filters(self, data: IpDefenderFiltersSchema, one: bool = True): 
        filters_to_dict = data.model_dump(exclude_none=True) 
        return await self.ip_def_repo.get_by_filters(filters_to_dict, one)

    async def decrease_attempt(self, ip: str) -> int: 
        return await self.ip_def_repo.decrease_attempt(ip) 
    
    async def set_applied_date_time(self, ip: str, date: datetime | None = None) -> int: 
        return await self.ip_def_repo.set_applied_date_time(ip, date)

    async def fill_attempt(self, ip: str) -> int: 
        return await self.ip_def_repo.fill_attempt(ip) 
