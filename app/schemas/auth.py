from pydantic import BaseModel, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    display_name: str
    account_type: str  # 'skater' or 'skateshop' - will be converted to is_shop boolean
    

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None