# AI-Enhanced Booking Optimization

Flask-based clinic appointment system that predicts patient no-shows, automates reminders, and keeps a privacy audit log designed around PIPEDA principles.

## Problem

Healthcare clinics lose capacity and revenue to missed appointments; staff need advance warning on high-risk bookings and automated multi-channel reminders without compromising patient privacy.

## Approach

Built a Flask + SQLAlchemy application with Random Forest no-show prediction (`MLService`) using booking lead time, day/time, patient history, appointment type, and seasonal features. Added SMS/email reminder scheduling (`ReminderService`), AES-backed privacy controls and audit logging (`PrivacyService`), and sample data for four clinic types (medical, physiotherapy, ## Results

- Working appointment, reminder, consent and audit-log features, with a dashboard and REST API.
- Sample data generator: 4 clinics, 24 patients, 350+ appointments.
- **No-show model: not ready.** With no real history, it trains on 1,000 generated appointments. On those it scores AUC 0.48 (0.5 is random) and 83.8% accuracy, below the 89.2% from always guessing "will attend". See `analysis/model_check.py`.

The earlier static demo showed 87.2% accuracy and a 94.2% reminder success rate. Those numbers were typed into the page, not measured, and were removed.

## Responsible AI, following the Reliable AI Adoption Framework

1. **Business problem:** reduce missed appointments with timely reminders, without treating any patient worse.
2. **Data readiness:** no real appointment history yet. The model trains on generated data, and its scores reflect that.
3. **Governance and risk:** health information falls under PIPEDA and provincial laws. Consent, encryption, audit and retention are built in. The design has not had a legal review.
4. **Technology and tools:** Flask, SQLAlchemy and a random forest, simple enough for a clinic's IT provider to run and inspect.
5. **People and adoption:** front-desk staff see the risk level and decide on extra contact. A score never blocks a booking.
6. **Outcomes and monitoring:** with real data, compare no-show rates for reminded and not-reminded patients, by group.

n policies, audit trail

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

**Project page:** https://danieldemoz.github.io/ai-booking-optimization/

Built by Daniel S. Demoz.
