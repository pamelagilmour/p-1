from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Import new modules
from models import UserRegister, UserLogin, TokenResponse, UserResponse
from auth import hash_password, verify_password, create_access_token, get_current_user

# Load environment vars
load_dotenv()

# Initialize app
app = FastAPI(title="AI Knowledge Base API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"], # The dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Database connection helper
def get_db_connection():
    """Create a database connection"""
    conn = psycopg2.connect(
        host="localhost",
        database="knowledge_base",
        user="",
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email, created_at",
            (user.email, hashed_password)
        )
        new_user = cursor.fetchone()
        
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

@app.get("/api/entries")
def get_entries(current_user: dict = Depends(get_current_user)):
    """
    Get all knowledge entries for the authenticated user
    This endpoint is now PROTECTED
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Only get entries for the current user
        cursor.execute(
            "SELECT * FROM knowledge_entries WHERE user_id = %s",
            (current_user['user_id'])
        )
        entries = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"entries": entries}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )