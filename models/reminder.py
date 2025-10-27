"""
Reminder Model for AI-Enhanced Booking Optimization System
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

# Import db from the main app
from app import db

class Reminder(db.Model):
    """Reminder model for tracking automated communications"""
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    reminder_type = Column(String(20), nullable=False)  # email, sms, chat
    scheduled_time = Column(DateTime, nullable=False)
    sent_time = Column(DateTime)
    status = Column(String(20), default='scheduled')  # scheduled, sent, failed, cancelled
    message_content = Column(Text)
    delivery_status = Column(String(50))  # delivered, failed, pending
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    appointment = relationship("Appointment", back_populates="reminders")
    
    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'reminder_type': self.reminder_type,
            'scheduled_time': self.scheduled_time.isoformat(),
            'sent_time': self.sent_time.isoformat() if self.sent_time else None,
            'status': self.status,
            'message_content': self.message_content,
            'delivery_status': self.delivery_status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Reminder {self.id} - {self.reminder_type}>'

