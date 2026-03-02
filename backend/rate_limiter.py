import redis
import time
from fastapi import HTTPException, status

# Use the same Redis client from cache_service
from cache_service import redis_client

class RateLimiter:
    """
    Token bucket rate limiter using Redis
    Default: 100 requests per minute per user
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def check_rate_limit(self, user_id: int) -> dict:
        """
        Check if user has exceeded rate limit
        Returns dict with: allowed (bool), remaining (int), reset_time (int)
        """
        key = f"rate_limit:user:{user_id}"
        current_time = int(time.time())
        
        # Get current count
        pipe = redis_client.pipeline()
        pipe.get(key)
        pipe.ttl(key)
        results = pipe.execute()
        
        current_count = int(results[0]) if results[0] else 0
        ttl = results[1]
        
        # If key doesn't exist or expired, start new window
        if current_count == 0 or ttl == -2:
            redis_client.setex(key, self.window_seconds, 1)
            return {
                "allowed": True,
                "remaining": self.max_requests - 1,
                "reset_time": current_time + self.window_seconds,
                "limit": self.max_requests
            }
        
        # Check if limit exceeded
        if current_count >= self.max_requests:
            reset_time = current_time + ttl
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": reset_time,
                "limit": self.max_requests
            }
        
        # Increment counter
        redis_client.incr(key)
        
        return {
            "allowed": True,
            "remaining": self.max_requests - current_count - 1,
            "reset_time": current_time + ttl,
            "limit": self.max_requests
        }

# Create rate limiter instances for different endpoints
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
auth_rate_limiter = RateLimiter(max_requests=5, window_seconds=900)  # 5 attempts per 15 min
chat_rate_limiter = RateLimiter(max_requests=10, window_seconds=3600)  # 10 per hour

def check_rate_limit(user_id: int):
    """
    Check rate limit and raise HTTPException if exceeded
    Use as: check_rate_limit(current_user['user_id'])
    """
    result = rate_limiter.check_rate_limit(user_id)
    
    if not result["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {result['reset_time'] - int(time.time())} seconds.",
            headers={
                "X-RateLimit-Limit": str(result["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(result["reset_time"]),
                "Retry-After": str(result["reset_time"] - int(time.time()))
            }
        )
    
    return result

def check_daily_ai_limit(user_id: int, limit: int = 20):
    """
    Check daily AI request limit (separate from general rate limit)
    Default: 20 AI requests per 24 hours
    
    Args:
        user_id: The user's ID
        limit: Maximum AI requests per day (default 20)
    
    Raises:
        HTTPException: If daily limit is exceeded
    """
    key = f"ai_limit:user:{user_id}:daily"
    window_seconds = 86400  # 24 hours
    current_time = int(time.time())
    
    # Get current count and TTL
    pipe = redis_client.pipeline()
    pipe.get(key)
    pipe.ttl(key)
    results = pipe.execute()
    
    current_count = int(results[0]) if results[0] else 0
    ttl = results[1]
    
    # If key doesn't exist or expired, start new window
    if current_count == 0 or ttl == -2:
        redis_client.setex(key, window_seconds, 1)
        return {
            "allowed": True,
            "remaining": limit - 1,
            "reset_time": current_time + window_seconds
        }
    
    # Check if limit exceeded
    if current_count >= limit:
        reset_time = current_time + ttl
        hours_remaining = ttl // 3600
        minutes_remaining = (ttl % 3600) // 60
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Daily AI request limit exceeded ({limit} requests per day). "
                   f"Resets in {hours_remaining}h {minutes_remaining}m.",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(ttl)
            }
        )
    
    # Increment counter
    redis_client.incr(key)
    
    return {
        "allowed": True,
        "remaining": limit - current_count - 1,
        "reset_time": current_time + ttl
    }

def check_auth_rate_limit(identifier: str):
    """
    Check authentication rate limit (by IP or email)
    Stricter limits to prevent brute force: 5 attempts per 15 minutes
    
    Args:
        identifier: IP address or email to rate limit
    
    Raises:
        HTTPException: If rate limit exceeded
    """
    result = auth_rate_limiter.check_rate_limit(identifier)
    
    if not result["allowed"]:
        minutes_remaining = (result["reset_time"] - int(time.time())) // 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Please try again in {minutes_remaining} minutes.",
            headers={
                "X-RateLimit-Limit": str(result["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(result["reset_time"]),
                "Retry-After": str(result["reset_time"] - int(time.time()))
            }
        )
    
    return result