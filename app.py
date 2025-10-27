"""
AI-Enhanced Booking Optimization for Clinics
Main Flask Application
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///clinic_booking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
from database import db
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database and models
from database import db, Patient, Appointment, Clinic, Reminder, AuditLog

# Import services
from services.ml_service import MLService
from services.reminder_service import ReminderService
from services.privacy_service import PrivacyService

# Initialize services
ml_service = MLService()
reminder_service = ReminderService()
privacy_service = PrivacyService()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/appointments')
def get_appointments():
    """Get appointments with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    appointments = Appointment.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'appointments': [appointment.to_dict() for appointment in appointments.items],
        'total': appointments.total,
        'pages': appointments.pages,
        'current_page': page
    })

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    """Create a new appointment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_id', 'clinic_id', 'appointment_time', 'appointment_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create appointment
        appointment = Appointment(
            patient_id=data['patient_id'],
            clinic_id=data['clinic_id'],
            appointment_time=datetime.fromisoformat(data['appointment_time']),
            appointment_type=data['appointment_type'],
            notes=data.get('notes', ''),
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Log the creation
        privacy_service.log_activity('appointment_created', appointment.id, request.remote_addr)
        
        # Schedule reminders
        reminder_service.schedule_reminders(appointment)
        
        return jsonify(appointment.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating appointment: {str(e)}")
        return jsonify({'error': 'Failed to create appointment'}), 500

@app.route('/api/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    """Update an appointment"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        data = request.get_json()
        
        # Update fields
        if 'appointment_time' in data:
            appointment.appointment_time = datetime.fromisoformat(data['appointment_time'])
        if 'status' in data:
            appointment.status = data['status']
        if 'notes' in data:
            appointment.notes = data['notes']
        
        appointment.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the update
        privacy_service.log_activity('appointment_updated', appointment_id, request.remote_addr)
        
        return jsonify(appointment.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        return jsonify({'error': 'Failed to update appointment'}), 500

@app.route('/api/analytics/no-show-predictions')
def get_no_show_predictions():
    """Get no-show predictions for upcoming appointments"""
    try:
        # Get upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.appointment_time >= datetime.now(),
            Appointment.status == 'scheduled'
        ).all()
        
        predictions = []
        for appointment in upcoming_appointments:
            prediction = ml_service.predict_no_show(appointment)
            predictions.append({
                'appointment_id': appointment.id,
                'patient_name': appointment.patient.name,
                'appointment_time': appointment.appointment_time.isoformat(),
                'no_show_probability': prediction['probability'],
                'risk_level': prediction['risk_level'],
                'recommended_actions': prediction['recommended_actions']
            })
        
        return jsonify(predictions)
        
    except Exception as e:
        logger.error(f"Error getting no-show predictions: {str(e)}")
        return jsonify({'error': 'Failed to get predictions'}), 500

@app.route('/api/analytics/dashboard-stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Calculate various metrics
        total_appointments = Appointment.query.count()
        upcoming_appointments = Appointment.query.filter(
            Appointment.appointment_time >= datetime.now(),
            Appointment.status == 'scheduled'
        ).count()
        
        # No-show rate (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_appointments = Appointment.query.filter(
            Appointment.appointment_time >= thirty_days_ago,
            Appointment.status.in_(['completed', 'no_show'])
        ).all()
        
        no_shows = len([a for a in recent_appointments if a.status == 'no_show'])
        no_show_rate = (no_shows / len(recent_appointments)) * 100 if recent_appointments else 0
        
        # Patient retention
        unique_patients = db.session.query(Patient.id).distinct().count()
        
        stats = {
            'total_appointments': total_appointments,
            'upcoming_appointments': upcoming_appointments,
            'no_show_rate': round(no_show_rate, 2),
            'total_patients': unique_patients,
            'high_risk_appointments': len([p for p in ml_service.get_high_risk_appointments() if p['risk_level'] == 'high'])
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard stats'}), 500

@app.route('/api/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create patient
        patient = Patient(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            date_of_birth=data.get('date_of_birth'),
            emergency_contact=data.get('emergency_contact'),
            medical_notes=data.get('medical_notes', ''),
            consent_given=data.get('consent_given', False)
        )
        
        db.session.add(patient)
        db.session.commit()
        
        # Log the creation
        privacy_service.log_activity('patient_created', patient.id, request.remote_addr)
        
        return jsonify(patient.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        return jsonify({'error': 'Failed to create patient'}), 500

@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient (PIPEDA compliant)"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Check if patient has consent for deletion
        if not patient.consent_given:
            return jsonify({'error': 'Patient consent required for deletion'}), 403
        
        # Log the deletion
        privacy_service.log_activity('patient_deleted', patient_id, request.remote_addr)
        
        # Soft delete - mark as deleted but keep for audit
        patient.deleted_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Patient deleted successfully'})
        
    except Exception as e:
        logger.error(f"Error deleting patient: {str(e)}")
        return jsonify({'error': 'Failed to delete patient'}), 500

@app.route('/api/reminders/send', methods=['POST'])
def send_reminder():
    """Manually send a reminder"""
    try:
        data = request.get_json()
        appointment_id = data.get('appointment_id')
        reminder_type = data.get('type', 'email')  # email, sms, chat
        
        appointment = Appointment.query.get_or_404(appointment_id)
        
        # Send reminder
        result = reminder_service.send_reminder(appointment, reminder_type)
        
        if result['success']:
            return jsonify({'message': 'Reminder sent successfully'})
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Error sending reminder: {str(e)}")
        return jsonify({'error': 'Failed to send reminder'}), 500

@app.route('/api/ml/retrain', methods=['POST'])
def retrain_model():
    """Retrain the no-show prediction model"""
    try:
        result = ml_service.retrain_model()
        
        if result['success']:
            return jsonify({'message': 'Model retrained successfully'})
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logger.error(f"Error retraining model: {str(e)}")
        return jsonify({'error': 'Failed to retrain model'}), 500

@app.route('/api/privacy/audit-logs')
def get_audit_logs():
    """Get audit logs for privacy compliance"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        return jsonify({'error': 'Failed to get audit logs'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create sample clinic
        clinic = Clinic(
            name="Sample Healthcare Clinic",
            address="123 Health St, City, Province",
            phone="(555) 123-4567",
            email="info@sampleclinic.com",
            specialties="Physiotherapy,Dental,Mental Health"
        )
        db.session.add(clinic)
        
        # Create sample patients
        patients = [
            Patient(
                name="John Doe",
                email="john.doe@email.com",
                phone="(555) 111-1111",
                date_of_birth=datetime(1985, 5, 15),
                consent_given=True
            ),
            Patient(
                name="Jane Smith",
                email="jane.smith@email.com",
                phone="(555) 222-2222",
                date_of_birth=datetime(1990, 8, 22),
                consent_given=True
            )
        ]
        
        for patient in patients:
            db.session.add(patient)
        
        db.session.commit()
        
        logger.info("Database initialized with sample data")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--init-db':
        init_db()
        sys.exit(0)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

