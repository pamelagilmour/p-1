## Production Deployment

**Redis Instance:** Railway Redis
**Connection:** Via `REDIS_URL` environment variable
**Memory Limit:** 256MB (Railway default)
**Eviction Policy:** allkeys-lru

### Monitoring

Check cache performance:
- Endpoint: `GET /api/cache/stats`
- Metrics tracked: hit rate, used memory, connected clients

### Cache Keys in Production

All cache keys are scoped by user ID to prevent data leakage:
- User entries are never cached across users
- Each user has isolated cache namespace
- Cache invalidation only affects the specific user's data