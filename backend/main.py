from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize app
app = FastAPI(title="AI Knowledge Base API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # The dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    return {
        "status": "healthy",
        "database": "not connected yet"
    }