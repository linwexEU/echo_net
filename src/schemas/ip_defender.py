from pydantic import BaseModel, Field 


class IpDefenderAddToDbSchema(BaseModel): 
    ip: str = Field(...)


class IpDefenderFiltersSchema(BaseModel): 
    ip: str | None = None 
