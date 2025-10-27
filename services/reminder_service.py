"""
Reminder Service for Automated Communications
"""

import os
import logging
from datetime import datetime, timedelta
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import requests
import json

logger = logging.getLogger(__name__)

class ReminderService:
    """Service for managing automated appointment reminders"""
    
    def __init__(self):
        # Twilio configuration for SMS
        self.twilio_client = None
        if os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN'):
            self.twilio_client = TwilioClient(
                os.getenv('TWILIO_ACCOUNT_SID'),
                os.getenv('TWILIO_AUTH_TOKEN')
            )
        
        # SendGrid configuration for email
        self.sendgrid_client = None
        if os.getenv('SENDGRID_API_KEY'):
            self.sendgrid_client = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@clinic.com')
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    
    def schedule_reminders(self, appointment):
        """Schedule all reminders for an appointment"""
        try:
            reminders = []
            
            # 72 hours before (for high-risk appointments)
            reminder_72h = self._create_reminder(
                appointment, 'email', 
                appointment.appointment_time - timedelta(hours=72),
                'early_reminder'
            )
            if reminder_72h:
                reminders.append(reminder_72h)
            
            # 48 hours before
            reminder_48h = self._create_reminder(
                appointment, 'email',
                appointment.appointment_time - timedelta(hours=48),
                'standard_reminder'
            )
            if reminder_48h:
                reminders.append(reminder_48h)
            
            # 24 hours before (SMS)
            reminder_24h = self._create_reminder(
                appointment, 'sms',
                appointment.appointment_time - timedelta(hours=24),
                'day_before_reminder'
            )
            if reminder_24h:
                reminders.append(reminder_24h)
            
            # 2 hours before (SMS)
            reminder_2h = self._create_reminder(
                appointment, 'sms',
                appointment.appointment_time - timedelta(hours=2),
                'final_reminder'
            )
            if reminder_2h:
                reminders.append(reminder_2h)
            
            logger.info(f"Scheduled {len(reminders)} reminders for appointment {appointment.id}")
            return reminders
            
        except Exception as e:
            logger.error(f"Error scheduling reminders: {str(e)}")
            return []
    
    def _create_reminder(self, appointment, reminder_type, scheduled_time, reminder_category):
        """Create a reminder record"""
        try:
            from models.reminder import Reminder
            
            message_content = self._generate_message_content(
                appointment, reminder_type, reminder_category
            )
            
            reminder = Reminder(
                appointment_id=appointment.id,
                reminder_type=reminder_type,
                scheduled_time=scheduled_time,
                message_content=message_content,
                status='scheduled'
            )
            
            return reminder
            
        except Exception as e:
            logger.error(f"Error creating reminder: {str(e)}")
            return None
    
    def _generate_message_content(self, appointment, reminder_type, category):
        """Generate appropriate message content based on type and category"""
        patient_name = appointment.patient.name
        appointment_time = appointment.appointment_time.strftime('%B %d, %Y at %I:%M %p')
        clinic_name = appointment.clinic.name
        appointment_type = appointment.appointment_type
        
        messages = {
            'early_reminder': {
                'email': f"""
Dear {patient_name},

This is a friendly reminder that you have an upcoming appointment:

Date & Time: {appointment_time}
Type: {appointment_type}
Location: {clinic_name}

Please confirm your attendance by replying to this email or calling us at {appointment.clinic.phone}.

If you need to reschedule, please contact us at least 24 hours in advance.

Best regards,
{clinic_name} Team
                """,
                'sms': f"Hi {patient_name}, you have an appointment on {appointment_time} at {clinic_name}. Please confirm by replying YES or call {appointment.clinic.phone} to reschedule."
            },
            'standard_reminder': {
                'email': f"""
Dear {patient_name},

Reminder: Your appointment is scheduled for {appointment_time}

Appointment Type: {appointment_type}
Location: {clinic_name}

Please arrive 15 minutes early for check-in. If you need to reschedule, please contact us at {appointment.clinic.phone}.

Thank you,
{clinic_name}
                """,
                'sms': f"Reminder: {patient_name}, your {appointment_type} appointment is tomorrow at {appointment_time} at {clinic_name}. Reply STOP to opt out."
            },
            'day_before_reminder': {
                'email': f"""
Dear {patient_name},

Final reminder: Your appointment is tomorrow at {appointment_time}

Please bring:
- Valid ID
- Insurance card (if applicable)
- List of current medications

If you need to reschedule, please call us immediately at {appointment.clinic.phone}.

See you tomorrow,
{clinic_name}
                """,
                'sms': f"Final reminder: {patient_name}, your appointment is tomorrow at {appointment_time} at {clinic_name}. Call {appointment.clinic.phone} if you need to reschedule."
            },
            'final_reminder': {
                'email': f"""
Dear {patient_name},

Your appointment is in 2 hours at {appointment_time}

Please arrive 15 minutes early for check-in.

We look forward to seeing you soon!

{clinic_name}
                """,
                'sms': f"Your appointment is in 2 hours at {appointment_time}. Please arrive 15 minutes early. {clinic_name}"
            }
        }
        
        return messages.get(category, {}).get(reminder_type, "Appointment reminder")
    
    def send_reminder(self, appointment, reminder_type='email'):
        """Send a reminder immediately"""
        try:
            if reminder_type == 'email':
                return self._send_email_reminder(appointment)
            elif reminder_type == 'sms':
                return self._send_sms_reminder(appointment)
            elif reminder_type == 'chat':
                return self._send_chat_reminder(appointment)
            else:
                return {'success': False, 'error': 'Invalid reminder type'}
                
        except Exception as e:
            logger.error(f"Error sending reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_email_reminder(self, appointment):
        """Send email reminder using SendGrid"""
        try:
            if not self.sendgrid_client:
                return {'success': False, 'error': 'SendGrid not configured'}
            
            message_content = self._generate_message_content(
                appointment, 'email', 'standard_reminder'
            )
            
            mail = Mail(
                from_email=self.from_email,
                to_emails=appointment.patient.email,
                subject=f"Appointment Reminder - {appointment.appointment_time.strftime('%B %d, %Y')}",
                html_content=message_content.replace('\n', '<br>')
            )
            
            response = self.sendgrid_client.send(mail)
            
            if response.status_code == 202:
                logger.info(f"Email reminder sent to {appointment.patient.email}")
                return {'success': True, 'message_id': response.headers.get('X-Message-Id')}
            else:
                return {'success': False, 'error': f'SendGrid error: {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error sending email reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_sms_reminder(self, appointment):
        """Send SMS reminder using Twilio"""
        try:
            if not self.twilio_client:
                return {'success': False, 'error': 'Twilio not configured'}
            
            message_content = self._generate_message_content(
                appointment, 'sms', 'day_before_reminder'
            )
            
            message = self.twilio_client.messages.create(
                body=message_content,
                from_=self.twilio_phone,
                to=appointment.patient.phone
            )
            
            logger.info(f"SMS reminder sent to {appointment.patient.phone}")
            return {'success': True, 'message_id': message.sid}
            
        except Exception as e:
            logger.error(f"Error sending SMS reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _send_chat_reminder(self, appointment):
        """Send chat reminder (placeholder for future integration)"""
        try:
            # This would integrate with chat platforms like WhatsApp Business API
            # For now, return a placeholder response
            
            logger.info(f"Chat reminder would be sent to {appointment.patient.name}")
            return {'success': True, 'message': 'Chat reminder sent (simulated)'}
            
        except Exception as e:
            logger.error(f"Error sending chat reminder: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_scheduled_reminders(self):
        """Process all scheduled reminders that are due"""
        try:
            from models.reminder import Reminder
            from models.appointment import Appointment
            
            # Get reminders that are due
            current_time = datetime.utcnow()
            due_reminders = Reminder.query.filter(
                Reminder.scheduled_time <= current_time,
                Reminder.status == 'scheduled'
            ).all()
            
            processed_count = 0
            
            for reminder in due_reminders:
                try:
                    # Get the appointment
                    appointment = Appointment.query.get(reminder.appointment_id)
                    if not appointment:
                        reminder.status = 'failed'
                        reminder.error_message = 'Appointment not found'
                        continue
                    
                    # Send the reminder
                    result = self.send_reminder(appointment, reminder.reminder_type)
                    
                    if result['success']:
                        reminder.status = 'sent'
                        reminder.sent_time = datetime.utcnow()
                        reminder.delivery_status = 'delivered'
                        processed_count += 1
                    else:
                        reminder.status = 'failed'
                        reminder.error_message = result['error']
                    
                except Exception as e:
                    logger.error(f"Error processing reminder {reminder.id}: {str(e)}")
                    reminder.status = 'failed'
                    reminder.error_message = str(e)
            
            # Commit all changes
            from app import db
            db.session.commit()
            
            logger.info(f"Processed {processed_count} reminders")
            return {'success': True, 'processed_count': processed_count}
            
        except Exception as e:
            logger.error(f"Error processing scheduled reminders: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_reminder_stats(self):
        """Get statistics about reminders"""
        try:
            from models.reminder import Reminder
            
            total_reminders = Reminder.query.count()
            sent_reminders = Reminder.query.filter(Reminder.status == 'sent').count()
            failed_reminders = Reminder.query.filter(Reminder.status == 'failed').count()
            scheduled_reminders = Reminder.query.filter(Reminder.status == 'scheduled').count()
            
            return {
                'total_reminders': total_reminders,
                'sent_reminders': sent_reminders,
                'failed_reminders': failed_reminders,
                'scheduled_reminders': scheduled_reminders,
                'success_rate': (sent_reminders / total_reminders * 100) if total_reminders > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting reminder stats: {str(e)}")
            return {'error': str(e)}
    
    def cancel_reminders(self, appointment_id):
        """Cancel all pending reminders for an appointment"""
        try:
            from models.reminder import Reminder
            
            reminders = Reminder.query.filter(
                Reminder.appointment_id == appointment_id,
                Reminder.status == 'scheduled'
            ).all()
            
            for reminder in reminders:
                reminder.status = 'cancelled'
            
            from app import db
            db.session.commit()
            
            logger.info(f"Cancelled {len(reminders)} reminders for appointment {appointment_id}")
            return {'success': True, 'cancelled_count': len(reminders)}
            
        except Exception as e:
            logger.error(f"Error cancelling reminders: {str(e)}")
            return {'success': False, 'error': str(e)}

