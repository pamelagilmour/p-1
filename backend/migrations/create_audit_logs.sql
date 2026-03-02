-- Audit Logs Table
-- Tracks security events and user actions for monitoring and compliance

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    user_email VARCHAR(255),
    ip_address VARCHAR(45),  -- IPv6 support
    event_type VARCHAR(50) NOT NULL,
    event_category VARCHAR(20) NOT NULL,  -- auth, api, security, system
    severity VARCHAR(10) NOT NULL,  -- info, warning, error, critical
    resource VARCHAR(100),  -- e.g., 'entry:123', 'user:456'
    action VARCHAR(50),  -- e.g., 'create', 'read', 'update', 'delete'
    status VARCHAR(20),  -- success, failure, blocked
    details JSONB,  -- Additional context
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast querying
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_severity ON audit_logs(severity);
CREATE INDEX idx_audit_logs_ip_address ON audit_logs(ip_address);
CREATE INDEX idx_audit_logs_category ON audit_logs(event_category);

-- Composite index for common queries
CREATE INDEX idx_audit_logs_user_time ON audit_logs(user_id, timestamp DESC);

-- Comments for documentation
COMMENT ON TABLE audit_logs IS 'Security audit trail for all important system events';
COMMENT ON COLUMN audit_logs.event_type IS 'Specific event: login_success, login_failed, rate_limit_exceeded, etc.';
COMMENT ON COLUMN audit_logs.event_category IS 'Broad category: auth, api, security, system';
COMMENT ON COLUMN audit_logs.severity IS 'Severity level: info, warning, error, critical';
COMMENT ON COLUMN audit_logs.details IS 'JSON object with additional context';
