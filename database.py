"""
Database initialization for AI-Enhanced Booking Optimization System
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Patient(db.Model):
    """Patient model with PIPEDA compliance features"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.DateTime)
    emergency_contact = db.Column(db.String(200))
    medical_notes = db.Column(db.Text)
    consent_given = db.Column(db.Boolean, default=False)
    consent_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime)  # Soft delete for audit trail
    
    # Relationships
    appointments = db.relationship("Appointment", back_populates="patient")
    
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

class Clinic(db.Model):
    """Clinic model"""
    __tablename__ = 'clinics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    specialties = db.Column(db.Text)  # JSON string of specialties
    operating_hours = db.Column(db.Text)  # JSON string of hours
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    appointments = db.relationship("Appointment", back_populates="clinic")
    
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

class Appointment(db.Model):
    """Appointment model with ML features"""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(50), nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled, no_show
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # ML features for no-show prediction
    booking_lead_time_hours = db.Column(db.Float)  # Hours between booking and appointment
    day_of_week = db.Column(db.Integer)  # 0-6 (Monday-Sunday)
    time_of_day = db.Column(db.Float)  # Hour of day (0-23.99)
    weather_condition = db.Column(db.String(20))  # sunny, rainy, snowy, etc.
    previous_no_shows = db.Column(db.Integer, default=0)
    appointment_frequency = db.Column(db.Float, default=0)  # Appointments per month
    
    # Relationships
    patient = db.relationship("Patient", back_populates="appointments")
    clinic = db.relationship("Clinic", back_populates="appointments")
    reminders = db.relationship("Reminder", back_populates="appointment")
    
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

class Reminder(db.Model):
    """Reminder model for tracking automated communications"""
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    reminder_type = db.Column(db.String(20), nullable=False)  # email, sms, chat
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, sent, failed, cancelled
    message_content = db.Column(db.Text)
    delivery_status = db.Column(db.String(50))  # delivered, failed, pending
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    appointment = db.relationship("Appointment", back_populates="reminders")
    
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

class AuditLog(db.Model):
    """Audit log for PIPEDA compliance"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)  # If user authentication is implemented
    action = db.Column(db.String(50), nullable=False)  # created, updated, deleted, accessed
    resource_type = db.Column(db.String(50), nullable=False)  # patient, appointment, etc.
    resource_id = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(45))  # IPv6 compatible
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    details = db.Column(db.Text)  # JSON string with additional details
    
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
