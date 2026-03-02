# Audit Logging System

## Overview

Comprehensive audit logging system that tracks all security-relevant events for monitoring, compliance, and incident response.

## What Gets Logged

### Authentication Events
- ✅ Successful logins
- ✅ Failed login attempts
- ✅ User registrations
- ✅ Invalid tokens

### API Events
- ✅ Entry creation, updates, deletion
- ✅ Unauthorized access attempts
- ✅ Rate limit violations
- ✅ AI chat requests

### Security Events
- ✅ Rate limit exceeded (global + per-endpoint)
- ✅ SQL injection attempts (detected in validation)
- ✅ XSS attempts (blocked by sanitization)
- ✅ Suspicious patterns

## Log Structure

Each audit log entry contains:

```json
{
  "id": 123,
  "timestamp": "2024-03-02T10:30:00Z",
  "user_id": 456,
  "user_email": "user@example.com",
  "ip_address": "192.168.1.1",
  "event_type": "login_success",
  "event_category": "auth",
  "severity": "info",
  "resource": "user:456",
  "action": "login",
  "status": "success",
  "details": {
    "reason": "valid_credentials"
  },
  "user_agent": "Mozilla/5.0..."
}
```

### Event Categories
- **auth**: Authentication and authorization
- **api**: API operations (CRUD)
- **security**: Security violations
- **system**: System events

### Severity Levels
- **info**: Normal operations
- **warning**: Suspicious but not critical
- **error**: Failed operations, errors
- **critical**: Security incidents

### Status Values
- **success**: Operation completed successfully
- **failure**: Operation failed
- **blocked**: Operation blocked by security rules

## API Endpoints

### View Your Activity
```
GET /api/my/audit-logs?limit=50
```

Returns your own audit log history.

### Admin: View All Logs
```
GET /api/admin/audit-logs?limit=100&severity=warning&user_id=123
```

Query params:
- `limit`: Number of logs (default 100, max 500)
- `severity`: Filter by severity (info, warning, error, critical)
- `user_id`: Filter by user ID

### Admin: Security Summary
```
GET /api/admin/security-summary?hours=24
```

Returns counts of security events in the last N hours.

Example response:
```json
{
  "period_hours": 24,
  "events": [
    {
      "event_type": "login_failed",
      "severity": "warning",
      "count": 15
    },
    {
      "event_type": "rate_limit_exceeded",
      "severity": "warning",
      "count": 8
    }
  ]
}
```

## Database Schema

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    user_email VARCHAR(255),
    ip_address VARCHAR(45),
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(20) NOT NULL,
    severity VARCHAR(10) NOT NULL,
    resource VARCHAR(100),
    action VARCHAR(50),
    status VARCHAR(20),
    details JSONB,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:** 7 indexes for fast querying on timestamp, user_id, event_type, severity, IP, category, and user+time composite.

## Usage in Code

### Log Authentication Events
```python
from audit_service import audit_logger

# Success
audit_logger.log_auth_success(
    user_id=user.id,
    user_email=user.email,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)

# Failure
audit_logger.log_auth_failure(
    user_email=email,
    ip_address=ip,
    reason="invalid_credentials",
    user_agent=user_agent
)
```

### Log Rate Limit Violations
```python
audit_logger.log_rate_limit(
    event_type=audit_logger.RATE_LIMIT_EXCEEDED,
    ip_address=client_ip,
    details={"endpoint": "/api/login"}
)
```

### Log Resource Actions
```python
audit_logger.log_resource_action(
    action="create",  # create, read, update, delete
    resource="entry:123",
    user_id=current_user['user_id'],
    ip_address=client_ip
)
```

### Custom Events
```python
audit_logger.log(
    event_type="custom_event",
    event_category=audit_logger.CATEGORY_SECURITY,
    severity=audit_logger.SEVERITY_WARNING,
    status=audit_logger.STATUS_BLOCKED,
    user_id=user_id,
    ip_address=ip,
    details={"custom_field": "value"}
)
```

## Monitoring Use Cases

### Detect Brute Force Attacks
Query failed login attempts from same IP:
```sql
SELECT ip_address, COUNT(*) as attempts
FROM audit_logs
WHERE event_type = 'login_failed'
AND timestamp > NOW() - INTERVAL '1 hour'
GROUP BY ip_address
HAVING COUNT(*) > 5
ORDER BY attempts DESC;
```

### Track User Activity
```sql
SELECT event_type, COUNT(*) as count
FROM audit_logs
WHERE user_id = 123
AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY event_type;
```

### Security Dashboard Metrics
- Failed login attempts (last 24h)
- Rate limit violations (last 24h)
- Unauthorized access attempts
- New user registrations
- Most active users

## Compliance Benefits

✅ **SOC 2 Type II**: Demonstrates logging and monitoring controls
✅ **GDPR**: Audit trail for data access and modifications
✅ **HIPAA**: Access logging for sensitive data
✅ **PCI DSS**: Authentication and authorization logging

## Retention Policy

**Recommended:**
- Keep last 90 days in hot storage (PostgreSQL)
- Archive older logs to cold storage (S3, log aggregation service)
- Delete logs older than 1-2 years (unless compliance requires longer)

**Future Enhancement:**
```sql
-- Automated cleanup (add to cron job)
DELETE FROM audit_logs 
WHERE timestamp < NOW() - INTERVAL '90 days';
```

## Performance

**Optimized for queries:**
- Index on timestamp (DESC) for recent logs
- Composite index on user_id + timestamp for user history
- Index on severity for security monitoring
- JSONB for flexible details storage

**Write performance:**
- Async logging (doesn't block requests)
- Graceful failure (logging errors don't crash app)
- Batching option for high-volume events (future)

## Migration

Run the migration:
```bash
cd backend
python run_audit_migration.py
```

Or manually:
```bash
psql -d knowledge_base -f migrations/create_audit_logs.sql
```
