from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from rate_limiter import check_rate_limit, rate_limiter
import time
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from typing import List
from cache_service import (
    get_cache, set_cache, delete_cache, 
    delete_cache_pattern, clear_user_cache, get_cache_stats
)

# Import new modules
from models import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    KnowledgeEntryCreate, KnowledgeEntryUpdate, KnowledgeEntryResponse,
    ChatMessage

)
from auth import hash_password, verify_password, create_access_token, get_current_user
from ai_service import chat_with_knowledge_base

# Load environment vars
load_dotenv()

# Initialize app
app = FastAPI(title="AI Knowledge Base API")


# Add middleware to track rate limits on all requests
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Add rate limit headers to all responses"""
    
    # Skip rate limiting for public endpoints
    public_paths = ["/", "/api/health", "/api/auth/register", "/api/auth/login", "/docs", "/openapi.json"]
    
    if request.url.path in public_paths:
        response = await call_next(request)
        return response
    
    # For protected endpoints, check if user is authenticated
    # We'll do the actual rate limit check in the dependency
    response = await call_next(request)
    return response

# Create dependency for rate limiting
def rate_limit_dependency(current_user: dict = Depends(get_current_user)):
    """
    Dependency that checks rate limit for authenticated user
    Use this in endpoints: Depends(rate_limit_dependency)
    """
    check_rate_limit(current_user['user_id'])
    return current_user

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://p-11-one.vercel.app",
        "https://p-11-one.vercel.app/",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Database connection helper
def get_db_connection():
    """Create a database connection"""

    # Use DATABASE_URL from environment (Railway sets this automatically)
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Railway/Production - use DATABASE_URL
        conn = psycopg2.connect(
            database_url,
            cursor_factory=RealDictCursor
        )
    else:
        # Local development - use individual params
        conn = psycopg2.connect(
            host="localhost",
            database="knowledge_base",
            user="",  # Your Mac username for local
            password="",
            cursor_factory=RealDictCursor
        )
    
    return conn

# Health check endpoint
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AI Knowledge Base API",
        "version": "0.0.0",
        "status": "running"
    }

@app.get("/api/health")
def health_check():
    """Health check endpoint, verify the server is running"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": f"error: {str(e)}"
        }

# Auth Endpoints

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    """Register a new user"""
    print(f"🔍 Register attempt for: {user.email}")
    
    try:
        conn = get_db_connection()
        print("✅ Database connected")
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        existing = cursor.fetchone()
        print(f"🔍 Existing user check: {existing}")
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = hash_password(user.password)
        print("✅ Password hashed")
        
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at",
            (user.email, hashed_password)
        )
        new_user = cursor.fetchone()
        print(f"✅ User created: {new_user}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return UserResponse(
            id=new_user['id'],
            email=new_user['email'],
            created_at=str(new_user['created_at'])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/auth/login", response_model=TokenResponse)
def login(user: UserLogin):
    """Login and get access token"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find user by email
        cursor.execute(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = %s",
            (user.email,)
        )
        db_user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Verify user exists and password is correct
        if not db_user or not verify_password(user.password, db_user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"user_id": db_user['id'], "email": db_user['email']}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=db_user['id'],
                email=db_user['email'],
                created_at=str(db_user['created_at'])
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user
    This endpoint is PROTECTED - requires valid JWT token
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user from database using user_id from token
        cursor.execute(
            "SELECT id, email, created_at FROM users WHERE id = %s",
            (current_user['user_id'],)
        )
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            created_at=str(user['created_at'])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Protected endpoint, entries
# Update get_entries endpoint with caching
@app.get("/api/entries", response_model=List[KnowledgeEntryResponse])
def get_entries(current_user: dict = Depends(rate_limit_dependency)):
    """Get all knowledge entries (cached + rate limited)"""
    
    # Check cache first
    cache_key = f"entries:user:{current_user['user_id']}:all"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    # Cache miss - fetch from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, user_id, title, content, tags, created_at, updated_at 
               FROM knowledge_entries 
               WHERE user_id = %s 
               ORDER BY created_at DESC""",
            (current_user['user_id'],)
        )
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        result = []
        for entry in entries:
            tags = entry['tags'] if entry['tags'] else []
            
            result.append(KnowledgeEntryResponse(
                id=entry['id'],
                user_id=entry['user_id'],
                title=entry['title'],
                content=entry['content'],
                tags=tags,
                created_at=str(entry['created_at']),
                updated_at=str(entry['updated_at'])
            ))
        
        # Convert to dict for caching
        result_dict = [
            {
                "id": e.id,
                "user_id": e.user_id,
                "title": e.title,
                "content": e.content,
                "tags": e.tags,
                "created_at": e.created_at,
                "updated_at": e.updated_at
            }
            for e in result
        ]
        
        # Cache for 15 minutes
        set_cache(cache_key, result_dict, ttl=900)
        
        return result
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Knowledge entries endpoints

# Update create_entry to invalidate cache
@app.post("/api/entries", response_model=KnowledgeEntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: KnowledgeEntryCreate,
    current_user: dict = Depends(rate_limit_dependency)
):
    """Create a new knowledge entry (invalidates cache)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO knowledge_entries (user_id, title, content, tags)
               VALUES (%s, %s, %s, %s)
               RETURNING id, user_id, title, content, tags, created_at, updated_at""",
            (current_user['user_id'], entry.title, entry.content, entry.tags)
        )
        new_entry = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Invalidate cache for this user
        clear_user_cache(current_user['user_id'])
        
        return KnowledgeEntryResponse(
            id=new_entry['id'],
            user_id=new_entry['user_id'],
            title=new_entry['title'],
            content=new_entry['content'],
            tags=new_entry['tags'] or [],
            created_at=str(new_entry['created_at']),
            updated_at=str(new_entry['updated_at'])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    """Create a new knowledge entry"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO knowledge_entries (user_id, title, content, tags)
               VALUES (%s, %s, %s, %s)
               RETURNING id, user_id, title, content, tags, created_at, updated_at""",
            (current_user['user_id'], entry.title, entry.content, entry.tags)
        )
        new_entry = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()

        # Invalidate this user's entries list cache
        cache_delete_pattern(f"entries:user:{current_user['user_id']}")
        
        return KnowledgeEntryResponse(
            id=new_entry['id'],
            user_id=new_entry['user_id'],
            title=new_entry['title'],
            content=new_entry['content'],
            tags=new_entry['tags'] or [],
            created_at=str(new_entry['created_at']),
            updated_at=str(new_entry['updated_at'])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/entries/{entry_id}", response_model=KnowledgeEntryResponse)
def get_entry(entry_id: int, current_user: dict = Depends(rate_limit_dependency)):
    """Get a specific knowledge entry"""
    
    cache_key = f"entry:{entry_id}:user:{current_user['user_id']}"
    cached = cache_get(cache_key)
    if cached:
        return cached

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, user_id, title, content, tags, created_at, updated_at
               FROM knowledge_entries
               WHERE id = %s AND user_id = %s""",
            (entry_id, current_user['user_id'])
        )
        entry = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        result = KnowledgeEntryResponse(
            id=entry['id'],
            user_id=entry['user_id'],
            title=entry['title'],
            content=entry['content'],
            tags=entry['tags'] or [],
            created_at=str(entry['created_at']),
            updated_at=str(entry['updated_at'])
        )
        
        cache_set(cache_key, result.model_dump(), ttl=300)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    """Get a specific knowledge entry"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, user_id, title, content, tags, created_at, updated_at
               FROM knowledge_entries
               WHERE id = %s AND user_id = %s""",
            (entry_id, current_user['user_id'])
        )
        entry = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        return KnowledgeEntryResponse(
            id=entry['id'],
            user_id=entry['user_id'],
            title=entry['title'],
            content=entry['content'],
            tags=entry['tags'] or [],
            created_at=str(entry['created_at']),
            updated_at=str(entry['updated_at'])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Update update_entry to invalidate cache
@app.put("/api/entries/{entry_id}", response_model=KnowledgeEntryResponse)
def update_entry(
    entry_id: int,
    entry_update: KnowledgeEntryUpdate,
    current_user: dict = Depends(rate_limit_dependency)
):
    """Update a knowledge entry (invalidates cache)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id FROM knowledge_entries WHERE id = %s AND user_id = %s",
            (entry_id, current_user['user_id'])
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        update_fields = []
        update_values = []
        
        if entry_update.title is not None:
            update_fields.append("title = %s")
            update_values.append(entry_update.title)
        
        if entry_update.content is not None:
            update_fields.append("content = %s")
            update_values.append(entry_update.content)
        
        if entry_update.tags is not None:
            update_fields.append("tags = %s")
            update_values.append(entry_update.tags)
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        update_values.append(entry_id)
        update_values.append(current_user['user_id'])
        
        query = f"""
            UPDATE knowledge_entries 
            SET {', '.join(update_fields)}
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, title, content, tags, created_at, updated_at
        """
        
        cursor.execute(query, update_values)
        updated_entry = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Invalidate cache for this user
        clear_user_cache(current_user['user_id'])
        
        return KnowledgeEntryResponse(
            id=updated_entry['id'],
            user_id=updated_entry['user_id'],
            title=updated_entry['title'],
            content=updated_entry['content'],
            tags=updated_entry['tags'] or [],
            created_at=str(updated_entry['created_at']),
            updated_at=str(updated_entry['updated_at'])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Update delete_entry to invalidate cache
@app.delete("/api/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, current_user: dict = Depends(rate_limit_dependency)):
    """Delete a knowledge entry (invalidates cache)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM knowledge_entries WHERE id = %s AND user_id = %s RETURNING id",
            (entry_id, current_user['user_id'])
        )
        deleted = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        # Invalidate cache for this user
        clear_user_cache(current_user['user_id'])
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Add cache stats endpoint
@app.get("/api/cache/stats")
def cache_stats(current_user: dict = Depends(get_current_user)):
    """Get Redis cache statistics (admin endpoint)"""
    return get_cache_stats()


@app.post("/api/chat")
def chat(
    request: Request,
    chat_message: ChatMessage,
    current_user: dict = Depends(rate_limit_dependency)
):
    """Send a message to Claude with knowledge base access"""
    try:
        response = chat_with_knowledge_base(
            message=chat_message.message,
            user_id=current_user['user_id']
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/rate-limit/status")
def rate_limit_status(current_user: dict = Depends(get_current_user)):
    """Get current rate limit status for user"""
    result = rate_limiter.check_rate_limit(current_user['user_id'])
    return {
        "user_id": current_user['user_id'],
        "requests_remaining": result['remaining'],
        "requests_limit": result['limit'],
        "reset_time": result['reset_time'],
        "reset_in_seconds": result['reset_time'] - int(time.time())
    }