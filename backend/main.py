from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

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

@app.get("/api/entries")
def get_entries():
    """Get all knowledge entries (test endpoint)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_entries")
        entries = cursor.fetchall()
        cursor.close()
        conn.close()

        return {"entries": entries}

    except Exception as e:
        return {"error": str(e)}