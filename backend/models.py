from pydantic import BaseModel, EmailStr, field_validator
import re
import html

class UserRegister(BaseModel):
    """Model for user registration"""
    email: EmailStr
    password: str
    website: str = "" # honeypot field

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 72:
            raise ValueError('Password cannot be longer than 72 characters (bcrypt limit)')
        
        # Password strength requirements
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        # Additional email validation beyond EmailStr
        if len(v) > 255:
            raise ValueError('Email cannot be longer than 255 characters')
        # Check for common SQL injection patterns in email
        dangerous_patterns = ['--', ';', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute']
        email_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in email_lower:
                raise ValueError('Invalid email format')
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
    
    @field_validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Title cannot be empty')
        if len(v) > 500:
            raise ValueError('Title cannot be longer than 500 characters')
        
        # Sanitize HTML to prevent XSS
        v = html.escape(v.strip())
        
        # Check for excessive whitespace or control characters
        if re.search(r'[\x00-\x1F\x7F-\x9F]', v):
            raise ValueError('Title contains invalid characters')
        
        return v
    
    @field_validator('content')
    def validate_content(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Content cannot be empty')
        if len(v) > 50000:
            raise ValueError('Content cannot be longer than 50,000 characters')
        
        # Sanitize HTML to prevent XSS (keep basic formatting)
        v = html.escape(v.strip())
        
        return v
    
    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Cannot have more than 10 tags')
        
        sanitized_tags = []
        for tag in v:
            if not tag or len(tag.strip()) == 0:
                continue  # Skip empty tags
            if len(tag) > 50:
                raise ValueError('Each tag must be 50 characters or less')
            
            # Sanitize and normalize tag
            clean_tag = html.escape(tag.strip().lower())
            
            # Check for invalid characters
            if not re.match(r'^[a-z0-9\s\-_]+$', clean_tag):
                raise ValueError(f'Tag "{tag}" contains invalid characters. Use only letters, numbers, spaces, hyphens, and underscores.')
            
            sanitized_tags.append(clean_tag)
        
        return sanitized_tags

class KnowledgeEntryUpdate(BaseModel):
    """Model for updating a knowledge entry"""
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    
    @field_validator('title')
    def validate_title(cls, v):
        if v is None:
            return v
        if len(v.strip()) < 1:
            raise ValueError('Title cannot be empty')
        if len(v) > 500:
            raise ValueError('Title cannot be longer than 500 characters')
        
        # Sanitize HTML
        v = html.escape(v.strip())
        
        # Check for control characters
        if re.search(r'[\x00-\x1F\x7F-\x9F]', v):
            raise ValueError('Title contains invalid characters')
        
        return v
    
    @field_validator('content')
    def validate_content(cls, v):
        if v is None:
            return v
        if len(v.strip()) < 1:
            raise ValueError('Content cannot be empty')
        if len(v) > 50000:
            raise ValueError('Content cannot be longer than 50,000 characters')
        
        # Sanitize HTML
        v = html.escape(v.strip())
        
        return v
    
    @field_validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError('Cannot have more than 10 tags')
        
        sanitized_tags = []
        for tag in v:
            if not tag or len(tag.strip()) == 0:
                continue
            if len(tag) > 50:
                raise ValueError('Each tag must be 50 characters or less')
            
            clean_tag = html.escape(tag.strip().lower())
            
            if not re.match(r'^[a-z0-9\s\-_]+$', clean_tag):
                raise ValueError(f'Tag "{tag}" contains invalid characters')
            
            sanitized_tags.append(clean_tag)
        
        return sanitized_tags

class KnowledgeEntryResponse(BaseModel):
    """Model for knowledge entry response"""
    id: int
    user_id: int
    title: str
    content: str
    tags: list[str]
    created_at: str
    updated_at: str

class ChatMessage(BaseModel):
    """Model for chat messages"""
    message: str
    
    @field_validator('message')
    def validate_message(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Message cannot be empty')
        if len(v) > 2000:
            raise ValueError('Message cannot be longer than 2,000 characters')
        
        # Sanitize HTML to prevent XSS
        v = html.escape(v.strip())
        
        # Check for control characters
        if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', v):
            raise ValueError('Message contains invalid characters')
        
        return v