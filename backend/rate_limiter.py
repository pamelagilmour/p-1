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

# Create rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

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
    
    # Log rate limit info
    print(f"⏱️  Rate limit check: user {user_id} - {result['remaining']}/{result['limit']} remaining")
    
    return result