from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Model for user response (no password!)"""
    id: int
    email: str
    created_at: str

class TokenResponse(BaseModel):
    """Model for token response"""
    access_token: str
    token_type: str
    user: UserResponse