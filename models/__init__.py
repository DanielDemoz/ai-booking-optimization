"""
Database Models for AI-Enhanced Booking Optimization System
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Patient(Base):
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

class Clinic(Base):
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

class Appointment(Base):
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

class Reminder(Base):
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

class AuditLog(Base):
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

class MLModel(Base):
    """Model metadata for tracking ML model versions"""
    __tablename__ = 'ml_models'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    model_path = Column(String(200), nullable=False)
    accuracy_score = Column(Float)
    training_data_size = Column(Integer)
    training_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    hyperparameters = Column(Text)  # JSON string
    feature_importance = Column(Text)  # JSON string
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'model_path': self.model_path,
            'accuracy_score': self.accuracy_score,
            'training_data_size': self.training_data_size,
            'training_date': self.training_date.isoformat(),
            'is_active': self.is_active,
            'hyperparameters': self.hyperparameters,
            'feature_importance': self.feature_importance
        }

