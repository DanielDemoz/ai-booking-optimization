"""
Clinic Model for AI-Enhanced Booking Optimization System
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

# Import db from the main app
from app import db

class Clinic(db.Model):
    """Clinic model"""
    __tablename__ = 'clinics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200))
    phone = Column(String(20))
    email = Column(String(120))
    specialties = Column(Text)  # JSON string of specialties
    operating_hours = Column(Text)  # JSON string of hours
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = relationship("Appointment", back_populates="clinic")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'specialties': self.specialties,
            'operating_hours': self.operating_hours,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Clinic {self.name}>'

