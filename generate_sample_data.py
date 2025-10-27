"""
Realistic Sample Data Generator for AI-Enhanced Booking Optimization System
This script creates comprehensive sample data for demonstration purposes
"""

import os
import random
import json
from datetime import datetime, timedelta
from database import db, Patient, Appointment, Clinic, Reminder, AuditLog

def generate_realistic_sample_data():
    """Generate comprehensive realistic sample data"""
    
    print("Generating realistic sample data for AI-Enhanced Booking Optimization System...")
    
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # 1. Create Multiple Clinics
    clinics = [
        Clinic(
            name="Downtown Medical Center",
            address="123 Main Street, Downtown, ON K1A 0A6",
            phone="(613) 555-0100",
            email="info@downtownmedical.ca",
            specialties="General Practice,Cardiology,Orthopedics",
            operating_hours='{"monday": "8:00-17:00", "tuesday": "8:00-17:00", "wednesday": "8:00-17:00", "thursday": "8:00-17:00", "friday": "8:00-17:00", "saturday": "9:00-13:00", "sunday": "closed"}'
        ),
        Clinic(
            name="Westside Physiotherapy Clinic",
            address="456 Oak Avenue, Westside, ON K2B 1C2",
            phone="(613) 555-0200",
            email="appointments@westsidephysio.ca",
            specialties="Physiotherapy,Sports Medicine,Rehabilitation",
            operating_hours='{"monday": "7:00-19:00", "tuesday": "7:00-19:00", "wednesday": "7:00-19:00", "thursday": "7:00-19:00", "friday": "7:00-18:00", "saturday": "8:00-16:00", "sunday": "closed"}'
        ),
        Clinic(
            name="Family Dental Care",
            address="789 Pine Street, Suburbia, ON K3C 2D3",
            phone="(613) 555-0300",
            email="hello@familydental.ca",
            specialties="General Dentistry,Orthodontics,Pediatric Dentistry",
            operating_hours='{"monday": "8:00-17:00", "tuesday": "8:00-17:00", "wednesday": "8:00-17:00", "thursday": "8:00-17:00", "friday": "8:00-16:00", "saturday": "9:00-14:00", "sunday": "closed"}'
        ),
        Clinic(
            name="Mental Health & Wellness Center",
            address="321 Elm Boulevard, Midtown, ON K4D 3E4",
            phone="(613) 555-0400",
            email="support@mentalwellness.ca",
            specialties="Psychology,Psychiatry,Counseling",
            operating_hours='{"monday": "9:00-18:00", "tuesday": "9:00-18:00", "wednesday": "9:00-18:00", "thursday": "9:00-18:00", "friday": "9:00-17:00", "saturday": "10:00-15:00", "sunday": "closed"}'
        )
    ]
    
    for clinic in clinics:
        db.session.add(clinic)
    db.session.commit()
    print(f"Created {len(clinics)} clinics")
    
    # 2. Create Diverse Patient Population
    patients_data = [
        # High-risk patients (frequent no-shows)
        {"name": "Sarah Johnson", "email": "sarah.j@email.com", "phone": "(613) 555-1001", "dob": (1985, 3, 15), "risk_profile": "high"},
        {"name": "Michael Chen", "email": "m.chen@email.com", "phone": "(613) 555-1002", "dob": (1992, 7, 22), "risk_profile": "high"},
        {"name": "Emily Rodriguez", "email": "emily.r@email.com", "phone": "(613) 555-1003", "dob": (1988, 11, 8), "risk_profile": "high"},
        
        # Medium-risk patients
        {"name": "David Thompson", "email": "david.t@email.com", "phone": "(613) 555-1004", "dob": (1975, 5, 30), "risk_profile": "medium"},
        {"name": "Lisa Wang", "email": "lisa.w@email.com", "phone": "(613) 555-1005", "dob": (1990, 9, 12), "risk_profile": "medium"},
        {"name": "James Wilson", "email": "james.w@email.com", "phone": "(613) 555-1006", "dob": (1983, 1, 25), "risk_profile": "medium"},
        
        # Low-risk patients (reliable)
        {"name": "Maria Garcia", "email": "maria.g@email.com", "phone": "(613) 555-1007", "dob": (1978, 12, 3), "risk_profile": "low"},
        {"name": "Robert Brown", "email": "robert.b@email.com", "phone": "(613) 555-1008", "dob": (1965, 8, 18), "risk_profile": "low"},
        {"name": "Jennifer Davis", "email": "jennifer.d@email.com", "phone": "(613) 555-1009", "dob": (1987, 4, 7), "risk_profile": "low"},
        
        # Elderly patients
        {"name": "Margaret Smith", "email": "margaret.s@email.com", "phone": "(613) 555-1010", "dob": (1955, 6, 14), "risk_profile": "medium"},
        {"name": "William Jones", "email": "william.j@email.com", "phone": "(613) 555-1011", "dob": (1948, 10, 29), "risk_profile": "low"},
        
        # Young adults
        {"name": "Alex Taylor", "email": "alex.t@email.com", "phone": "(613) 555-1012", "dob": (1995, 2, 16), "risk_profile": "high"},
        {"name": "Sophie Anderson", "email": "sophie.a@email.com", "phone": "(613) 555-1013", "dob": (1998, 12, 21), "risk_profile": "medium"},
        
        # Working professionals
        {"name": "Kevin Lee", "email": "kevin.l@email.com", "phone": "(613) 555-1014", "dob": (1980, 3, 9), "risk_profile": "low"},
        {"name": "Amanda White", "email": "amanda.w@email.com", "phone": "(613) 555-1015", "dob": (1985, 11, 5), "risk_profile": "medium"},
        
        # Parents with children
        {"name": "Christopher Miller", "email": "chris.m@email.com", "phone": "(613) 555-1016", "dob": (1982, 7, 13), "risk_profile": "medium"},
        {"name": "Jessica Taylor", "email": "jessica.t@email.com", "phone": "(613) 555-1017", "dob": (1989, 5, 27), "risk_profile": "low"},
        
        # Students
        {"name": "Ryan Murphy", "email": "ryan.m@email.com", "phone": "(613) 555-1018", "dob": (2000, 8, 31), "risk_profile": "high"},
        {"name": "Olivia Clark", "email": "olivia.c@email.com", "phone": "(613) 555-1019", "dob": (1999, 1, 11), "risk_profile": "medium"},
        
        # Additional diverse patients
        {"name": "Ahmed Hassan", "email": "ahmed.h@email.com", "phone": "(613) 555-1020", "dob": (1976, 9, 4), "risk_profile": "low"},
        {"name": "Priya Patel", "email": "priya.p@email.com", "phone": "(613) 555-1021", "dob": (1984, 6, 19), "risk_profile": "medium"},
        {"name": "Jean-Pierre Dubois", "email": "jp.dubois@email.com", "phone": "(613) 555-1022", "dob": (1979, 4, 2), "risk_profile": "low"},
        {"name": "Yuki Tanaka", "email": "yuki.t@email.com", "phone": "(613) 555-1023", "dob": (1991, 10, 15), "risk_profile": "medium"},
        {"name": "Isabella Silva", "email": "isabella.s@email.com", "phone": "(613) 555-1024", "dob": (1986, 12, 8), "risk_profile": "high"},
    ]
    
    patients = []
    for patient_data in patients_data:
        patient = Patient(
            name=patient_data["name"],
            email=patient_data["email"],
            phone=patient_data["phone"],
            date_of_birth=datetime(*patient_data["dob"]),
            consent_given=True,
            consent_date=datetime.now() - timedelta(days=random.randint(1, 365)),
            medical_notes=f"Risk profile: {patient_data['risk_profile']}"
        )
        patients.append(patient)
        db.session.add(patient)
    
    db.session.commit()
    print(f"Created {len(patients)} diverse patients")
    
    # 3. Create Realistic Appointment History and Future Appointments
    appointment_types = [
        "consultation", "follow_up", "treatment", "checkup", "emergency", 
        "therapy", "surgery", "diagnostic", "preventive", "rehabilitation"
    ]
    
    # Generate historical appointments (last 6 months)
    historical_appointments = []
    for i in range(200):  # 200 historical appointments
        patient = random.choice(patients)
        clinic = random.choice(clinics)
        
        # Random date in the past 6 months
        days_ago = random.randint(1, 180)
        appointment_time = datetime.now() - timedelta(days=days_ago)
        
        # Adjust appointment time to business hours
        hour = random.randint(8, 17)
        minute = random.choice([0, 15, 30, 45])
        appointment_time = appointment_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Determine status based on risk profile
        risk_profile = patient.medical_notes.split(": ")[1] if patient.medical_notes else "medium"
        
        if risk_profile == "high":
            status = random.choices(
                ["completed", "no_show", "cancelled"], 
                weights=[60, 25, 15]
            )[0]
        elif risk_profile == "medium":
            status = random.choices(
                ["completed", "no_show", "cancelled"], 
                weights=[75, 15, 10]
            )[0]
        else:  # low risk
            status = random.choices(
                ["completed", "no_show", "cancelled"], 
                weights=[90, 5, 5]
            )[0]
        
        appointment = Appointment(
            patient_id=patient.id,
            clinic_id=clinic.id,
            appointment_time=appointment_time,
            appointment_type=random.choice(appointment_types),
            duration_minutes=random.choice([30, 45, 60, 90]),
            status=status,
            notes=f"Historical appointment - {status}",
            booking_lead_time_hours=random.uniform(1, 168),  # 1 hour to 1 week
            day_of_week=appointment_time.weekday(),
            time_of_day=appointment_time.hour + appointment_time.minute / 60.0,
            weather_condition=random.choice(["sunny", "rainy", "cloudy", "snowy"]),
            previous_no_shows=random.randint(0, 5) if risk_profile == "high" else random.randint(0, 2),
            appointment_frequency=random.uniform(0.5, 4.0)
        )
        historical_appointments.append(appointment)
        db.session.add(appointment)
    
    # Generate future appointments (next 3 months)
    future_appointments = []
    for i in range(150):  # 150 future appointments
        patient = random.choice(patients)
        clinic = random.choice(clinics)
        
        # Random date in the next 3 months
        days_ahead = random.randint(1, 90)
        appointment_time = datetime.now() + timedelta(days=days_ahead)
        
        # Adjust appointment time to business hours
        hour = random.randint(8, 17)
        minute = random.choice([0, 15, 30, 45])
        appointment_time = appointment_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # All future appointments start as scheduled
        appointment = Appointment(
            patient_id=patient.id,
            clinic_id=clinic.id,
            appointment_time=appointment_time,
            appointment_type=random.choice(appointment_types),
            duration_minutes=random.choice([30, 45, 60, 90]),
            status="scheduled",
            notes="Future appointment",
            booking_lead_time_hours=random.uniform(1, 168),
            day_of_week=appointment_time.weekday(),
            time_of_day=appointment_time.hour + appointment_time.minute / 60.0,
            weather_condition=random.choice(["sunny", "rainy", "cloudy", "snowy"]),
            previous_no_shows=random.randint(0, 5) if patient.medical_notes and "high" in patient.medical_notes else random.randint(0, 2),
            appointment_frequency=random.uniform(0.5, 4.0)
        )
        future_appointments.append(appointment)
        db.session.add(appointment)
    
    db.session.commit()
    print(f"Created {len(historical_appointments)} historical appointments")
    print(f"Created {len(future_appointments)} future appointments")
    
    # 4. Create Sample Reminders
    reminders = []
    for appointment in future_appointments[:50]:  # Create reminders for first 50 future appointments
        # 72 hours before
        reminder_72h = Reminder(
            appointment_id=appointment.id,
            reminder_type="email",
            scheduled_time=appointment.appointment_time - timedelta(hours=72),
            status="scheduled",
            message_content=f"Early reminder for {appointment.patient.name}"
        )
        reminders.append(reminder_72h)
        db.session.add(reminder_72h)
        
        # 24 hours before
        reminder_24h = Reminder(
            appointment_id=appointment.id,
            reminder_type="sms",
            scheduled_time=appointment.appointment_time - timedelta(hours=24),
            status="scheduled",
            message_content=f"SMS reminder for {appointment.patient.name}"
        )
        reminders.append(reminder_24h)
        db.session.add(reminder_24h)
    
    db.session.commit()
    print(f"Created {len(reminders)} scheduled reminders")
    
    # 5. Create Sample Audit Logs
    audit_logs = []
    for i in range(100):
        log = AuditLog(
            action=random.choice(["created", "updated", "accessed", "deleted"]),
            resource_type=random.choice(["patient", "appointment", "reminder"]),
            resource_id=random.randint(1, 50),
            ip_address=f"192.168.1.{random.randint(1, 254)}",
            user_agent="AI-Booking-System/1.0",
            details=json.dumps({"timestamp": datetime.now().isoformat()})
        )
        audit_logs.append(log)
        db.session.add(log)
    
    db.session.commit()
    print(f"Created {len(audit_logs)} audit log entries")
    
    print("\nRealistic sample data generation complete!")
    print("\nSummary:")
    print(f"   • {len(clinics)} clinics (Medical, Physio, Dental, Mental Health)")
    print(f"   • {len(patients)} diverse patients (various risk profiles)")
    print(f"   • {len(historical_appointments)} historical appointments")
    print(f"   • {len(future_appointments)} future appointments")
    print(f"   • {len(reminders)} scheduled reminders")
    print(f"   • {len(audit_logs)} audit log entries")
    
    print("\nKey Features Demonstrated:")
    print("   • High-risk patients with frequent no-shows")
    print("   • Medium-risk patients with occasional issues")
    print("   • Low-risk reliable patients")
    print("   • Diverse appointment types and times")
    print("   • Realistic booking patterns")
    print("   • Comprehensive audit trail")
    
    print("\nReady for demonstration!")
    print("   • AI predictions will show realistic risk levels")
    print("   • Dashboard will display meaningful analytics")
    print("   • Reminder system has scheduled communications")
    print("   • Privacy compliance features are active")

if __name__ == "__main__":
    # Import the Flask app to get the database context
    from app import app
    with app.app_context():
        generate_realistic_sample_data()
