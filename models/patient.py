"""
Patient Model for AI-Enhanced Booking Optimization System
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship

# Import db from the main app
from app import db

class Patient(db.Model):
    """Patient model with PIPEDA compliance features"""
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)
    date_of_birth = Column(DateTime)
    emergency_contact = Column(String(200))
    medical_notes = Column(Text)
    consent_given = Column(Boolean, default=False)
    consent_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)  # Soft delete for audit trail
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'emergency_contact': self.emergency_contact,
            'medical_notes': self.medical_notes,
            'consent_given': self.consent_given,
            'consent_date': self.consent_date.isoformat() if self.consent_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Patient {self.name}>'

