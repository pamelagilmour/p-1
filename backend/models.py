from pydantic import BaseModel, EmailStr, field_validator

class UserRegister(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        print(f"DEBUG: Password value: {v}")
        print(f"DEBUG: Password length: {len(v)}")
        print(f"DEBUG: Password type: {type(v)}")

        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 72:
            raise ValueError('Password cannot be longer than 72 characters')
        return v

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