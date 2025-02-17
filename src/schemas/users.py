from pydantic import BaseModel, Field, EmailStr 


class UsersAddSchema(BaseModel): 
    username: str = Field(..., min_length=4)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=6)


class UsersAddToDbSchema(BaseModel): 
    username: str = Field(..., min_length=4)
    email: EmailStr = Field(...)
    hashed_password: str = Field(...)


class UsersRegisterResponse(BaseModel): 
    user_id: int


class UsersFiltersSchema(BaseModel): 
    id: int | None = None 
    username: int | None = None 
    email: EmailStr | None = None 


class UsersUpdateSchema(BaseModel): 
    username: int | None = Field(None, min_length=6) 
    email: EmailStr | None = None
    bio: str | None = None
    hashed_password: str | None = None


class UsersAuthSchema(BaseModel): 
    email: EmailStr = Field(...) 
    password: str = Field(...) 


class UsersAuthResponseSchema(BaseModel): 
    AccessToken: str = Field(...) 


class UsersIconResponseSchema(BaseModel): 
    user_id: int = Field(...)


class UsersInfoSchema(BaseModel): 
    username: str = Field(...) 
    bio: str | None = None
    email: EmailStr = Field(...)


class ResetPasswordSchema(BaseModel): 
    new_password: str = Field(...) 


class AddBioSchema(BaseModel): 
    bio: str = Field(...) 
