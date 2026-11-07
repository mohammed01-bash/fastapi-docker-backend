from pydantic import EmailStr , BaseModel , Field 
from typing import Optional


class UserCreate(BaseModel):
    username: str =Field(...,min_length=3)
    email: EmailStr
    password:str=Field(...,min_length=6)
    age:int=Field(...,ge=18)

class UserUpdate(BaseModel):
    username:Optional[str]=Field(None,min_length=3)
    email:Optional[EmailStr]=None
    age:Optional[int]=Field(None,ge=18)

class UserResponse(BaseModel):
    id:int 
    username:str
    email:str
    age:Optional[int]
    is_active:bool

class UserLogin(BaseModel):
    email:str
    password:str
    

class PostCreate(BaseModel):
    title: str
    content : str
 
class PostResponse(BaseModel):
    id:int
    title:str
    content:str
    author_id:int

class PostUpdate(BaseModel):
    title:str

class Config:
    from_attributes=True
