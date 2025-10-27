"""
Configuration settings for AI-Enhanced Booking Optimization System
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///clinic_booking.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Machine Learning Configuration
    ML_MODEL_PATH = os.environ.get('ML_MODEL_PATH', 'models/no_show_model.pkl')
    RETRAIN_THRESHOLD = int(os.environ.get('RETRAIN_THRESHOLD', 100))
    
    # Communication Services
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@clinic.com')
    
    # Privacy & Compliance
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 2555))  # 7 years
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    AUDIT_LOG_ENABLED = os.environ.get('AUDIT_LOG_ENABLED', 'true').lower() == 'true'
    
    # Dashboard Configuration
    DASHBOARD_REFRESH_INTERVAL = int(os.environ.get('DASHBOARD_REFRESH_INTERVAL', 300))  # 5 minutes
    MAX_APPOINTMENTS_PER_PAGE = int(os.environ.get('MAX_APPOINTMENTS_PER_PAGE', 50))
    
    # Reminder Configuration
    REMINDER_TIMES = {
        'early': timedelta(hours=72),      # 3 days before
        'standard': timedelta(hours=48),   # 2 days before
        'day_before': timedelta(hours=24), # 1 day before
        'final': timedelta(hours=2)        # 2 hours before
    }
    
    # Risk Level Thresholds
    RISK_THRESHOLDS = {
        'low': 0.1,      # < 10% probability
        'medium': 0.25,  # 10-25% probability
        'high': 1.0      # > 25% probability
    }
    
    # Appointment Types
    APPOINTMENT_TYPES = [
        'consultation',
        'follow_up',
        'treatment',
        'emergency',
        'checkup',
        'therapy',
        'surgery'
    ]
    
    # Clinic Specialties
    CLINIC_SPECIALTIES = [
        'Physiotherapy',
        'Dental',
        'Mental Health',
        'Chiropractic',
        'General Practice',
        'Specialist Consultation',
        'Emergency Care'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with production settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@localhost/clinic_booking'
    
    # Ensure encryption is enabled in production
    if not Config.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

