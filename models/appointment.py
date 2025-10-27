"""
Appointment Model for AI-Enhanced Booking Optimization System
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

# Import db from the main app
from app import db

class Appointment(db.Model):
    """Appointment model with ML features"""
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    clinic_id = Column(Integer, ForeignKey('clinics.id'), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    appointment_type = Column(String(50), nullable=False)
    duration_minutes = Column(Integer, default=60)
    status = Column(String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled, no_show
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ML features for no-show prediction
    booking_lead_time_hours = Column(Float)  # Hours between booking and appointment
    day_of_week = Column(Integer)  # 0-6 (Monday-Sunday)
    time_of_day = Column(Float)  # Hour of day (0-23.99)
    weather_condition = Column(String(20))  # sunny, rainy, snowy, etc.
    previous_no_shows = Column(Integer, default=0)
    appointment_frequency = Column(Float, default=0)  # Appointments per month
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    clinic = relationship("Clinic", back_populates="appointments")
    reminders = relationship("Reminder", back_populates="appointment")
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'clinic_id': self.clinic_id,
            'patient_name': self.patient.name if self.patient else None,
            'clinic_name': self.clinic.name if self.clinic else None,
            'appointment_time': self.appointment_time.isoformat(),
            'appointment_type': self.appointment_type,
            'duration_minutes': self.duration_minutes,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'booking_lead_time_hours': self.booking_lead_time_hours,
            'day_of_week': self.day_of_week,
            'time_of_day': self.time_of_day,
            'weather_condition': self.weather_condition,
            'previous_no_shows': self.previous_no_shows,
            'appointment_frequency': self.appointment_frequency
        }
    
    def __repr__(self):
        return f'<Appointment {self.id} - {self.appointment_time}>'

