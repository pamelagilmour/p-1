from pydantic import BaseModel, EmailStr, field_validator, validator

class UserRegister(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v):
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

class KnowledgeEntryCreate(BaseModel):
    """Model for creating a knowledge entry"""
    title: str
    content: str
    tags: list[str] = []
    
    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1:
            raise ValueError('Title cannot be empty')
        if len(v) > 500:
            raise ValueError('Title cannot be longer than 500 characters')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if len(v) < 1:
            raise ValueError('Content cannot be empty')
        return v

class KnowledgeEntryUpdate(BaseModel):
    """Model for updating a knowledge entry"""
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None

class KnowledgeEntryResponse(BaseModel):
    """Model for knowledge entry response"""
    id: int
    user_id: int
    title: str
    content: str
    tags: list[str]
    created_at: str
    updated_at: str