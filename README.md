# AI-Enhanced Booking Optimization

Flask-based clinic appointment system that predicts patient no-shows, automates reminders, and tracks PIPEDA-compliant audit logs.

## Problem

Healthcare clinics lose capacity and revenue to missed appointments; staff need advance warning on high-risk bookings and automated multi-channel reminders without compromising patient privacy.

## Approach

Built a Flask + SQLAlchemy application with Random Forest no-show prediction (`MLService`) using booking lead time, day/time, patient history, appointment type, and seasonal features. Added SMS/email reminder scheduling (`ReminderService`), AES-backed privacy controls and audit logging (`PrivacyService`), and sample data for four clinic types (medical, physiotherapy, dental, mental health).

## Results

- No-show risk scoring with Low / Medium / High categories per appointment
- Dashboard API for appointments, predictions, reminders, and compliance metrics
- Sample dataset: 4 clinics, 24 patients, 350+ appointments, 100+ scheduled reminders
- PIPEDA-oriented features: encryption, consent handling, retention policies, audit trail

## Tech stack

Python, Flask, SQLAlchemy, scikit-learn (RandomForestClassifier), pandas, SQLite

## How to run

```bash
git clone https://github.com/DanielDemoz/ai-booking-optimization.git
cd ai-booking-optimization
pip install -r requirements.txt
cp env.example .env
python app.py --init-db
python app.py
```

Open http://localhost:5000

Tests: `python -m pytest tests/`

## Screenshot / demo

**Static interactive demo:** https://danieldemoz.github.io/ai-booking-optimization/

Built by Daniel S. Demoz for healthcare clinic booking optimization.
