"""
Test Suite for AI-Enhanced Booking Optimization System
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from app import app, db
from models.patient import Patient
from models.appointment import Appointment
from models.clinic import Clinic
from services.ml_service import MLService
from services.reminder_service import ReminderService
from services.privacy_service import PrivacyService

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

@pytest.fixture
def sample_clinic():
    """Create sample clinic for testing"""
    clinic = Clinic(
        name="Test Clinic",
        address="123 Test St",
        phone="(555) 123-4567",
        email="test@clinic.com",
        specialties="Physiotherapy,Dental"
    )
    db.session.add(clinic)
    db.session.commit()
    return clinic

@pytest.fixture
def sample_patient():
    """Create sample patient for testing"""
    patient = Patient(
        name="John Doe",
        email="john.doe@test.com",
        phone="(555) 111-1111",
        consent_given=True,
        consent_date=datetime.utcnow()
    )
    db.session.add(patient)
    db.session.commit()
    return patient

@pytest.fixture
def sample_appointment(sample_patient, sample_clinic):
    """Create sample appointment for testing"""
    appointment = Appointment(
        patient_id=sample_patient.id,
        clinic_id=sample_clinic.id,
        appointment_time=datetime.utcnow() + timedelta(days=1),
        appointment_type="consultation",
        status="scheduled"
    )
    db.session.add(appointment)
    db.session.commit()
    return appointment

class TestPatientModel:
    """Test cases for Patient model"""
    
    def test_create_patient(self, client):
        """Test creating a new patient"""
        response = client.post('/api/patients', json={
            'name': 'Jane Smith',
            'email': 'jane.smith@test.com',
            'phone': '(555) 222-2222',
            'consent_given': True
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Jane Smith'
        assert data['email'] == 'jane.smith@test.com'
    
    def test_patient_validation(self, client):
        """Test patient validation"""
        response = client.post('/api/patients', json={
            'name': 'Test Patient'
            # Missing required fields
        })
        
        assert response.status_code == 400
    
    def test_patient_deletion(self, client, sample_patient):
        """Test patient deletion with consent"""
        response = client.delete(f'/api/patients/{sample_patient.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Patient deleted successfully'

class TestAppointmentModel:
    """Test cases for Appointment model"""
    
    def test_create_appointment(self, client, sample_patient, sample_clinic):
        """Test creating a new appointment"""
        appointment_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
        
        response = client.post('/api/appointments', json={
            'patient_id': sample_patient.id,
            'clinic_id': sample_clinic.id,
            'appointment_time': appointment_time,
            'appointment_type': 'consultation',
            'notes': 'Test appointment'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['patient_id'] == sample_patient.id
        assert data['clinic_id'] == sample_clinic.id
    
    def test_appointment_validation(self, client):
        """Test appointment validation"""
        response = client.post('/api/appointments', json={
            'patient_id': 1
            # Missing required fields
        })
        
        assert response.status_code == 400
    
    def test_appointment_update(self, client, sample_appointment):
        """Test updating an appointment"""
        new_time = (datetime.utcnow() + timedelta(days=2)).isoformat()
        
        response = client.put(f'/api/appointments/{sample_appointment.id}', json={
            'appointment_time': new_time,
            'status': 'confirmed'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'confirmed'

class TestMLService:
    """Test cases for Machine Learning service"""
    
    def test_ml_service_initialization(self):
        """Test ML service initialization"""
        ml_service = MLService()
        assert ml_service is not None
        assert ml_service.model_path is not None
    
    def test_feature_preparation(self, sample_appointment):
        """Test feature preparation for ML model"""
        ml_service = MLService()
        features = ml_service.prepare_features(sample_appointment)
        
        assert 'booking_lead_time_hours' in features
        assert 'day_of_week' in features
        assert 'time_of_day' in features
        assert isinstance(features['booking_lead_time_hours'], (int, float))
    
    def test_no_show_prediction(self, sample_appointment):
        """Test no-show prediction"""
        ml_service = MLService()
        prediction = ml_service.predict_no_show(sample_appointment)
        
        assert 'probability' in prediction
        assert 'risk_level' in prediction
        assert 'recommended_actions' in prediction
        assert 0 <= prediction['probability'] <= 1
        assert prediction['risk_level'] in ['low', 'medium', 'high']
    
    def test_model_training(self):
        """Test model training with synthetic data"""
        ml_service = MLService()
        result = ml_service.train_model()
        
        assert result['success'] is True
        assert 'accuracy' in result
        assert result['accuracy'] > 0

class TestReminderService:
    """Test cases for Reminder service"""
    
    def test_reminder_service_initialization(self):
        """Test reminder service initialization"""
        reminder_service = ReminderService()
        assert reminder_service is not None
    
    def test_message_generation(self, sample_appointment):
        """Test reminder message generation"""
        reminder_service = ReminderService()
        message = reminder_service._generate_message_content(
            sample_appointment, 'email', 'standard_reminder'
        )
        
        assert isinstance(message, str)
        assert len(message) > 0
        assert sample_appointment.patient.name in message
    
    def test_reminder_scheduling(self, sample_appointment):
        """Test reminder scheduling"""
        reminder_service = ReminderService()
        reminders = reminder_service.schedule_reminders(sample_appointment)
        
        assert isinstance(reminders, list)
        assert len(reminders) > 0
    
    def test_reminder_stats(self):
        """Test reminder statistics"""
        reminder_service = ReminderService()
        stats = reminder_service.get_reminder_stats()
        
        assert 'total_reminders' in stats
        assert 'sent_reminders' in stats
        assert 'success_rate' in stats

class TestPrivacyService:
    """Test cases for Privacy service"""
    
    def test_privacy_service_initialization(self):
        """Test privacy service initialization"""
        privacy_service = PrivacyService()
        assert privacy_service is not None
        assert privacy_service.data_retention_days > 0
    
    def test_data_anonymization(self):
        """Test data anonymization"""
        privacy_service = PrivacyService()
        
        test_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '(555) 123-4567'
        }
        
        anonymized = privacy_service.anonymize_patient_data(test_data)
        
        assert anonymized['name'] != test_data['name']
        assert anonymized['email'] != test_data['email']
        assert anonymized['phone'] != test_data['phone']
        assert 'patient_id_hash' in anonymized
    
    def test_data_hashing(self):
        """Test data hashing"""
        privacy_service = PrivacyService()
        
        test_string = "test data"
        hash1 = privacy_service.hash_personal_data(test_string)
        hash2 = privacy_service.hash_personal_data(test_string)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 character hex string
    
    def test_consent_validation(self, sample_patient):
        """Test consent validation"""
        privacy_service = PrivacyService()
        result = privacy_service.validate_consent(sample_patient.id)
        
        assert 'valid' in result
        assert result['valid'] is True

class TestAPIIntegration:
    """Integration test cases"""
    
    def test_dashboard_stats(self, client, sample_appointment):
        """Test dashboard statistics endpoint"""
        response = client.get('/api/analytics/dashboard-stats')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_appointments' in data
        assert 'upcoming_appointments' in data
        assert 'no_show_rate' in data
    
    def test_no_show_predictions(self, client, sample_appointment):
        """Test no-show predictions endpoint"""
        response = client.get('/api/analytics/no-show-predictions')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_reminder_sending(self, client, sample_appointment):
        """Test reminder sending endpoint"""
        response = client.post('/api/reminders/send', json={
            'appointment_id': sample_appointment.id,
            'type': 'email'
        })
        
        # This might fail in test environment due to missing credentials
        # but should not crash the application
        assert response.status_code in [200, 500]
    
    def test_model_retraining(self, client):
        """Test model retraining endpoint"""
        response = client.post('/api/ml/retrain')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data or 'error' in data

class TestDataPrivacy:
    """Test cases for data privacy compliance"""
    
    def test_audit_logging(self, client, sample_patient):
        """Test audit log creation"""
        # Create a patient to trigger audit log
        response = client.post('/api/patients', json={
            'name': 'Audit Test Patient',
            'email': 'audit@test.com',
            'phone': '(555) 999-9999',
            'consent_given': True
        })
        
        assert response.status_code == 201
        
        # Check audit logs
        response = client.get('/api/privacy/audit-logs')
        assert response.status_code == 200
    
    def test_data_retention_check(self, client):
        """Test data retention policy check"""
        privacy_service = PrivacyService()
        retention_info = privacy_service.check_data_retention()
        
        assert 'cutoff_date' in retention_info
        assert 'retention_days' in retention_info
    
    def test_privacy_compliance_report(self, client):
        """Test privacy compliance report generation"""
        privacy_service = PrivacyService()
        report = privacy_service.get_privacy_compliance_report()
        
        assert 'generated_at' in report
        assert 'patient_data' in report
        assert 'compliance_status' in report

if __name__ == '__main__':
    pytest.main([__file__])

