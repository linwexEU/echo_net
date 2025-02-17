from pydantic import BaseModel, Field 


class ReportedUserAddToDb(BaseModel): 
    reporter_id: int = Field(...) 
    user_id: int = Field(...)


class ReportedUserFilters(BaseModel):
    id: int | None = None 
    reporter_id: int | None = None 
    user_id: int | None = None


class ReportedUserResponse(BaseModel): 
    report_id: int = Field(...) 
