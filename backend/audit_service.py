"""
Audit Logging Service
Tracks security events and user actions for monitoring and compliance
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from datetime import datetime
import json

load_dotenv()

class AuditLogger:
    """Central audit logging service"""
    
    # Event types
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    REGISTER_SUCCESS = "register_success"
    REGISTER_FAILED = "register_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    AUTH_RATE_LIMIT_EXCEEDED = "auth_rate_limit_exceeded"
    
    ENTRY_CREATED = "entry_created"
    ENTRY_UPDATED = "entry_updated"
    ENTRY_DELETED = "entry_deleted"
    ENTRY_ACCESSED = "entry_accessed"
    
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    INVALID_TOKEN = "invalid_token"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    
    AI_CHAT_REQUEST = "ai_chat_request"
    AI_LIMIT_EXCEEDED = "ai_limit_exceeded"
    
    # Categories
    CATEGORY_AUTH = "auth"
    CATEGORY_API = "api"
    CATEGORY_SECURITY = "security"
    CATEGORY_SYSTEM = "system"
    
    # Severity levels
    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_ERROR = "error"
    SEVERITY_CRITICAL = "critical"
    
    # Status
    STATUS_SUCCESS = "success"
    STATUS_FAILURE = "failure"
    STATUS_BLOCKED = "blocked"
    
    def __init__(self):
        """Initialize audit logger with database connection"""
        self.database_url = os.getenv("DATABASE_URL")
    
    def _get_connection(self):
        """Get database connection"""
        if self.database_url:
            return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
        else:
            return psycopg2.connect(
                host="localhost",
                database="knowledge_base",
                user="",
                password="",
                cursor_factory=RealDictCursor
            )
    
    def log(
        self,
        event_type: str,
        event_category: str,
        severity: str,
        status: str,
        ip_address: Optional[str] = None,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log an audit event
        
        Args:
            event_type: Specific event (e.g., 'login_success')
            event_category: Category (auth, api, security, system)
            severity: Severity level (info, warning, error, critical)
            status: Event status (success, failure, blocked)
            ip_address: Client IP address
            user_id: User ID (if authenticated)
            user_email: User email
            resource: Resource being accessed (e.g., 'entry:123')
            action: Action performed (create, read, update, delete)
            details: Additional context as dict
            user_agent: User agent string
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO audit_logs (
                    user_id, user_email, ip_address, event_type, event_category,
                    severity, resource, action, status, details, user_agent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    user_email,
                    ip_address,
                    event_type,
                    event_category,
                    severity,
                    resource,
                    action,
                    status,
                    json.dumps(details) if details else None,
                    user_agent
                )
            )
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            # Audit logging should never break the application
            # Log to stderr but don't raise
            import sys
            print(f"Audit logging error: {e}", file=sys.stderr)
    
    def log_auth_success(self, user_id: int, user_email: str, ip_address: str, user_agent: Optional[str] = None):
        """Log successful authentication"""
        self.log(
            event_type=self.LOGIN_SUCCESS,
            event_category=self.CATEGORY_AUTH,
            severity=self.SEVERITY_INFO,
            status=self.STATUS_SUCCESS,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_auth_failure(self, user_email: str, ip_address: str, reason: str, user_agent: Optional[str] = None):
        """Log failed authentication attempt"""
        self.log(
            event_type=self.LOGIN_FAILED,
            event_category=self.CATEGORY_AUTH,
            severity=self.SEVERITY_WARNING,
            status=self.STATUS_FAILURE,
            user_email=user_email,
            ip_address=ip_address,
            details={"reason": reason},
            user_agent=user_agent
        )
    
    def log_rate_limit(self, event_type: str, ip_address: str, user_id: Optional[int] = None, details: Optional[Dict] = None):
        """Log rate limit violation"""
        self.log(
            event_type=event_type,
            event_category=self.CATEGORY_SECURITY,
            severity=self.SEVERITY_WARNING,
            status=self.STATUS_BLOCKED,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )
    
    def log_unauthorized_access(self, user_id: int, resource: str, ip_address: str):
        """Log unauthorized access attempt"""
        self.log(
            event_type=self.UNAUTHORIZED_ACCESS,
            event_category=self.CATEGORY_SECURITY,
            severity=self.SEVERITY_ERROR,
            status=self.STATUS_BLOCKED,
            user_id=user_id,
            resource=resource,
            ip_address=ip_address
        )
    
    def log_resource_action(self, action: str, resource: str, user_id: int, ip_address: str, status: str = STATUS_SUCCESS):
        """Log CRUD action on a resource"""
        event_map = {
            "create": self.ENTRY_CREATED,
            "update": self.ENTRY_UPDATED,
            "delete": self.ENTRY_DELETED,
            "read": self.ENTRY_ACCESSED
        }
        
        self.log(
            event_type=event_map.get(action, "resource_action"),
            event_category=self.CATEGORY_API,
            severity=self.SEVERITY_INFO,
            status=status,
            user_id=user_id,
            resource=resource,
            action=action,
            ip_address=ip_address
        )
    
    def get_recent_logs(self, limit: int = 100, user_id: Optional[int] = None, severity: Optional[str] = None):
        """
        Retrieve recent audit logs
        
        Args:
            limit: Maximum number of logs to return
            user_id: Filter by user ID
            severity: Filter by severity level
        
        Returns:
            List of audit log entries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            if severity:
                query += " AND severity = %s"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            logs = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [dict(log) for log in logs]
        except Exception as e:
            print(f"Error fetching audit logs: {e}")
            return []
    
    def get_security_summary(self, hours: int = 24):
        """
        Get security event summary for the last N hours
        
        Returns:
            Dict with counts of security events
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    event_type,
                    severity,
                    COUNT(*) as count
                FROM audit_logs
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                AND event_category IN ('auth', 'security')
                GROUP BY event_type, severity
                ORDER BY count DESC
                """,
                (hours,)
            )
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error fetching security summary: {e}")
            return []

# Global audit logger instance
audit_logger = AuditLogger()
