import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Redis client
# Railway provides REDIS_URL or individual host/port
redis_url = os.getenv("REDIS_URL")

def get_cache(key: str):
    """Get value from cache"""
    try:
        value = redis_client.get(key)
        if value:
            print(f"✅ Cache HIT: {key}")
            return json.loads(value)
        print(f"❌ Cache MISS: {key}")
        return None
    except Exception as e:
        print(f"Cache error: {e}")
        return None

if redis_url:
    # Use connection URL (Railway format)
    redis_client = redis.from_url(redis_url, decode_responses=True)
else:
    # Use individual params (fallback for local dev)
    redis_client = redis.Redis(
        host=os.getenv("REDISHOST", "localhost"),
        port=int(os.getenv("REDISPORT", 6379)),
        db=0,
        decode_responses=True
    )

def set_cache(key: str, value: any, ttl: int = 900):
    """
    Set value in cache with TTL (time to live)
    Default TTL: 900 seconds (15 minutes)
    """
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)  # default=str handles datetime
        )
        print(f"💾 Cache SET: {key} (TTL: {ttl}s)")
        return True
    except Exception as e:
        print(f"Cache error: {e}")
        return False

def delete_cache(key: str):
    """Delete a specific cache key"""
    try:
        redis_client.delete(key)
        print(f"🗑️  Cache DELETE: {key}")
        return True
    except Exception as e:
        print(f"Cache error: {e}")
        return False

def delete_cache_pattern(pattern: str):
    """Delete all keys matching a pattern (e.g., 'entries:user:*')"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            print(f"🗑️  Cache DELETE pattern: {pattern} ({len(keys)} keys)")
        return True
    except Exception as e:
        print(f"Cache error: {e}")
        return False

def clear_user_cache(user_id: int):
    """Clear all cache for a specific user"""
    patterns = [
        f"entries:user:{user_id}:*",
        f"entry:*:user:{user_id}",
        f"chat:user:{user_id}:*"
    ]
    for pattern in patterns:
        delete_cache_pattern(pattern)

def get_cache_stats():
    """Get Redis stats for monitoring"""
    try:
        info = redis_client.info()
        return {
            "used_memory": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": calculate_hit_rate(
                info.get("keyspace_hits", 0),
                info.get("keyspace_misses", 0)
            )
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_hit_rate(hits: int, misses: int) -> str:
    """Calculate cache hit rate percentage"""
    total = hits + misses
    if total == 0:
        return "0%"
    rate = (hits / total) * 100
    return f"{rate:.1f}%"
