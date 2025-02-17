from pydantic import BaseModel, Field 


class PasswordResetAddToDb(BaseModel): 
    user_id: int = Field(...)
    pin_code: int = Field(...)


class PasswordResetFilters(BaseModel): 
    id: int | None = None 
    user_id: int | None = None 


class PasswordResetPayload(BaseModel): 
    password: str = Field(...)


class PasswordResetResponse(BaseModel): 
    user_id: int = Field(...)
