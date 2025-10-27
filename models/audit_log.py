"""
Audit Log Model for PIPEDA Compliance
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text

# Import db from the main app
from app import db

class AuditLog(db.Model):
    """Audit log for PIPEDA compliance"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)  # If user authentication is implemented
    action = Column(String(50), nullable=False)  # created, updated, deleted, accessed
    resource_type = Column(String(50), nullable=False)  # patient, appointment, etc.
    resource_id = Column(Integer, nullable=False)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)  # JSON string with additional details
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.resource_type}:{self.resource_id}>'

