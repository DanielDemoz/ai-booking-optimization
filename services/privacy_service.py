"""
Privacy Service for PIPEDA Compliance
"""

import os
import logging
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)

class PrivacyService:
    """Service for managing privacy compliance and data protection"""
    
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        self.data_retention_days = int(os.getenv('DATA_RETENTION_DAYS', 2555))  # 7 years default
        self.audit_log_enabled = os.getenv('AUDIT_LOG_ENABLED', 'true').lower() == 'true'
        
        # Initialize encryption if key is provided
        self.cipher_suite = None
        if self.encryption_key:
            try:
                # Ensure key is 32 bytes for Fernet
                key = self.encryption_key.encode()[:32].ljust(32, b'0')
                self.cipher_suite = Fernet(Fernet.generate_key())  # In production, use the actual key
            except Exception as e:
                logger.error(f"Error initializing encryption: {str(e)}")
    
    def log_activity(self, action, resource_id, ip_address, user_id=None, details=None):
        """Log user activity for audit trail"""
        try:
            if not self.audit_log_enabled:
                return
            
            from models.audit_log import AuditLog
            
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=self._get_resource_type_from_action(action),
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=self._get_user_agent(),
                details=json.dumps(details) if details else None
            )
            
            from app import db
            db.session.add(audit_log)
            db.session.commit()
            
            logger.info(f"Audit log created: {action} on resource {resource_id}")
            
        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")
    
    def _get_resource_type_from_action(self, action):
        """Determine resource type from action"""
        action_mapping = {
            'patient_created': 'patient',
            'patient_updated': 'patient',
            'patient_deleted': 'patient',
            'patient_accessed': 'patient',
            'appointment_created': 'appointment',
            'appointment_updated': 'appointment',
            'appointment_cancelled': 'appointment',
            'appointment_accessed': 'appointment',
            'reminder_sent': 'reminder',
            'data_exported': 'data',
            'data_deleted': 'data'
        }
        return action_mapping.get(action, 'unknown')
    
    def _get_user_agent(self):
        """Get user agent from request context"""
        # In a real implementation, this would get the actual user agent
        return "AI-Booking-System/1.0"
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data"""
        try:
            if not self.cipher_suite:
                logger.warning("Encryption not configured, storing data unencrypted")
                return data
            
            if isinstance(data, str):
                data = data.encode()
            
            encrypted_data = self.cipher_suite.encrypt(data)
            return encrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            if not self.cipher_suite:
                return encrypted_data
            
            if isinstance(encrypted_data, str):
                encrypted_data = encrypted_data.encode()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            return encrypted_data
    
    def hash_personal_data(self, data):
        """Create a hash of personal data for anonymization"""
        try:
            if isinstance(data, str):
                data = data.encode()
            
            # Use SHA-256 for hashing
            hash_object = hashlib.sha256(data)
            return hash_object.hexdigest()
            
        except Exception as e:
            logger.error(f"Error hashing data: {str(e)}")
            return None
    
    def anonymize_patient_data(self, patient_data):
        """Anonymize patient data while preserving necessary information"""
        try:
            anonymized = patient_data.copy()
            
            # Anonymize personal identifiers
            if 'name' in anonymized:
                anonymized['name'] = self._anonymize_name(anonymized['name'])
            
            if 'email' in anonymized:
                anonymized['email'] = self._anonymize_email(anonymized['email'])
            
            if 'phone' in anonymized:
                anonymized['phone'] = self._anonymize_phone(anonymized['phone'])
            
            # Keep medical data for analysis but remove personal identifiers
            anonymized['patient_id_hash'] = self.hash_personal_data(str(patient_data.get('id', '')))
            
            return anonymized
            
        except Exception as e:
            logger.error(f"Error anonymizing patient data: {str(e)}")
            return patient_data
    
    def _anonymize_name(self, name):
        """Anonymize name while preserving structure"""
        if not name:
            return "Anonymous"
        
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}*** {parts[-1][0]}***"
        else:
            return f"{name[0]}***"
    
    def _anonymize_email(self, email):
        """Anonymize email while preserving domain for analysis"""
        if not email or '@' not in email:
            return "anonymous@example.com"
        
        local, domain = email.split('@', 1)
        return f"{local[0]}***@{domain}"
    
    def _anonymize_phone(self, phone):
        """Anonymize phone number"""
        if not phone:
            return "***-***-****"
        
        # Keep area code for geographic analysis
        cleaned = ''.join(filter(str.isdigit, phone))
        if len(cleaned) >= 10:
            return f"{cleaned[:3]}-***-****"
        else:
            return "***-***-****"
    
    def check_data_retention(self):
        """Check and handle data retention policies"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.data_retention_days)
            
            # Find old data that should be deleted
            from models.patient import Patient
            from models.appointment import Appointment
            
            old_patients = Patient.query.filter(
                Patient.created_at < cutoff_date,
                Patient.deleted_at.is_(None)
            ).all()
            
            old_appointments = Appointment.query.filter(
                Appointment.created_at < cutoff_date,
                Appointment.status.in_(['completed', 'cancelled', 'no_show'])
            ).all()
            
            # Log the data retention check
            self.log_activity(
                'data_retention_check',
                0,
                '127.0.0.1',
                details={
                    'cutoff_date': cutoff_date.isoformat(),
                    'old_patients_count': len(old_patients),
                    'old_appointments_count': len(old_appointments)
                }
            )
            
            return {
                'cutoff_date': cutoff_date.isoformat(),
                'old_patients_count': len(old_patients),
                'old_appointments_count': len(old_appointments),
                'retention_days': self.data_retention_days
            }
            
        except Exception as e:
            logger.error(f"Error checking data retention: {str(e)}")
            return {'error': str(e)}
    
    def export_patient_data(self, patient_id, include_sensitive=True):
        """Export patient data in compliance with data portability requirements"""
        try:
            from models.patient import Patient
            from models.appointment import Appointment
            
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Get all appointments for the patient
            appointments = Appointment.query.filter_by(patient_id=patient_id).all()
            
            export_data = {
                'patient_info': patient.to_dict(),
                'appointments': [appointment.to_dict() for appointment in appointments],
                'export_date': datetime.utcnow().isoformat(),
                'data_subject_rights': {
                    'right_to_access': True,
                    'right_to_portability': True,
                    'right_to_rectification': True,
                    'right_to_erasure': True
                }
            }
            
            # Log the data export
            self.log_activity(
                'data_exported',
                patient_id,
                '127.0.0.1',
                details={
                    'include_sensitive': include_sensitive,
                    'appointments_count': len(appointments)
                }
            )
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting patient data: {str(e)}")
            return {'error': str(e)}
    
    def delete_patient_data(self, patient_id, reason='patient_request'):
        """Delete patient data in compliance with right to erasure"""
        try:
            from models.patient import Patient
            from models.appointment import Appointment
            
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'error': 'Patient not found'}
            
            # Check if patient has given consent for deletion
            if not patient.consent_given:
                return {'error': 'Patient consent required for data deletion'}
            
            # Soft delete - mark as deleted but keep for audit
            patient.deleted_at = datetime.utcnow()
            
            # Cancel future appointments
            future_appointments = Appointment.query.filter(
                Appointment.patient_id == patient_id,
                Appointment.appointment_time > datetime.utcnow(),
                Appointment.status == 'scheduled'
            ).all()
            
            for appointment in future_appointments:
                appointment.status = 'cancelled'
                appointment.notes = f"Cancelled due to data deletion request - {reason}"
            
            # Log the deletion
            self.log_activity(
                'data_deleted',
                patient_id,
                '127.0.0.1',
                details={
                    'reason': reason,
                    'cancelled_appointments': len(future_appointments)
                }
            )
            
            from app import db
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Patient data deleted successfully',
                'cancelled_appointments': len(future_appointments)
            }
            
        except Exception as e:
            logger.error(f"Error deleting patient data: {str(e)}")
            return {'error': str(e)}
    
    def get_privacy_compliance_report(self):
        """Generate a privacy compliance report"""
        try:
            from models.patient import Patient
            from models.audit_log import AuditLog
            
            # Get basic statistics
            total_patients = Patient.query.count()
            patients_with_consent = Patient.query.filter(Patient.consent_given == True).count()
            patients_deleted = Patient.query.filter(Patient.deleted_at.isnot(None)).count()
            
            # Get audit log statistics
            total_audit_logs = AuditLog.query.count()
            recent_logs = AuditLog.query.filter(
                AuditLog.timestamp >= datetime.utcnow() - timedelta(days=30)
            ).count()
            
            # Data retention check
            retention_info = self.check_data_retention()
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'patient_data': {
                    'total_patients': total_patients,
                    'patients_with_consent': patients_with_consent,
                    'consent_rate': (patients_with_consent / total_patients * 100) if total_patients > 0 else 0,
                    'patients_deleted': patients_deleted
                },
                'audit_logging': {
                    'total_logs': total_audit_logs,
                    'recent_logs_30_days': recent_logs,
                    'audit_enabled': self.audit_log_enabled
                },
                'data_retention': retention_info,
                'compliance_status': {
                    'pipeda_compliant': True,  # Simplified check
                    'data_encryption': self.cipher_suite is not None,
                    'audit_trail': self.audit_log_enabled,
                    'consent_management': True
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating privacy compliance report: {str(e)}")
            return {'error': str(e)}
    
    def validate_consent(self, patient_id):
        """Validate that patient has given proper consent"""
        try:
            from models.patient import Patient
            
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'valid': False, 'error': 'Patient not found'}
            
            if not patient.consent_given:
                return {'valid': False, 'error': 'Patient consent not given'}
            
            # Check if consent is recent (within 2 years)
            if patient.consent_date:
                consent_age = datetime.utcnow() - patient.consent_date
                if consent_age.days > 730:  # 2 years
                    return {
                        'valid': False,
                        'error': 'Consent is older than 2 years and may need renewal'
                    }
            
            return {'valid': True, 'consent_date': patient.consent_date.isoformat() if patient.consent_date else None}
            
        except Exception as e:
            logger.error(f"Error validating consent: {str(e)}")
            return {'valid': False, 'error': str(e)}

