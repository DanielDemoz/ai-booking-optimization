# AI-Enhanced Booking Optimization System
## Installation and Deployment Guide

### Prerequisites

Before installing the AI-Enhanced Booking Optimization System, ensure you have:

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git** (for version control)
- **SQLite** (included with Python) or **PostgreSQL** (for production)
- **Web browser** (Chrome, Firefox, Safari, or Edge)

### System Requirements

**Minimum Requirements:**
- 4GB RAM
- 2GB free disk space
- Internet connection for external services

**Recommended Requirements:**
- 8GB RAM
- 10GB free disk space
- Stable internet connection
- Dedicated server for production

---

## Installation Steps

### Step 1: Download the System

```bash
# Clone the repository
git clone https://github.com/your-org/ai-booking-optimization.git
cd ai-booking-optimization

# Or download and extract the ZIP file
# Extract to your desired location
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your configuration
# Use a text editor to modify the values
```

**Required Configuration:**

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///clinic_booking.db

# Twilio SMS Configuration (Optional)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# SendGrid Email Configuration (Optional)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@yourclinic.com

# Privacy & Compliance
DATA_RETENTION_DAYS=2555
ENCRYPTION_KEY=your-32-character-encryption-key
AUDIT_LOG_ENABLED=true
```

### Step 5: Initialize Database

```bash
# Initialize database with sample data
python app.py --init-db

# Verify database creation
ls -la *.db
```

### Step 6: Start the Application

```bash
# Start the Flask application
python app.py

# The application will be available at:
# http://localhost:5000
```

### Step 7: Verify Installation

1. **Open your web browser**
2. **Navigate to** `http://localhost:5000`
3. **Check the dashboard loads correctly**
4. **Verify sample data is present**

---

## Production Deployment

### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With configuration file
gunicorn -c gunicorn.conf.py app:app
```

**Gunicorn Configuration (`gunicorn.conf.py`):**

```python
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

### Using Docker

**Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**Docker Compose (`docker-compose.yml`):**

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/clinic_booking
    depends_on:
      - db
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=clinic_booking
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Deploy with Docker:**

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Using Nginx (Reverse Proxy)

**Nginx Configuration (`/etc/nginx/sites-available/clinic-ai`):**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable the site:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/clinic-ai /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## Database Setup

### SQLite (Development)

SQLite is included with Python and requires no additional setup:

```bash
# Database file will be created automatically
# Location: clinic_booking.db
```

### PostgreSQL (Production)

**Install PostgreSQL:**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib

# macOS
brew install postgresql
```

**Create Database:**

```sql
-- Connect to PostgreSQL
sudo -u postgres psql

-- Create database and user
CREATE DATABASE clinic_booking;
CREATE USER clinic_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE clinic_booking TO clinic_user;

-- Exit
\q
```

**Update Configuration:**

```env
DATABASE_URL=postgresql://clinic_user:secure_password@localhost:5432/clinic_booking
```

---

## External Service Setup

### Twilio (SMS Reminders)

1. **Create Twilio Account**
   - Visit [twilio.com](https://www.twilio.com)
   - Sign up for an account
   - Verify your phone number

2. **Get Credentials**
   - Account SID: Found in Twilio Console Dashboard
   - Auth Token: Found in Twilio Console Dashboard
   - Phone Number: Purchase a Twilio phone number

3. **Configure System**
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### SendGrid (Email Reminders)

1. **Create SendGrid Account**
   - Visit [sendgrid.com](https://www.sendgrid.com)
   - Sign up for an account
   - Verify your email address

2. **Create API Key**
   - Go to Settings → API Keys
   - Create a new API key with "Full Access"
   - Copy the API key

3. **Configure System**
   ```env
   SENDGRID_API_KEY=SG.your_api_key_here
   FROM_EMAIL=noreply@yourclinic.com
   ```

### Weather API (Optional)

For enhanced no-show predictions:

1. **OpenWeatherMap**
   - Sign up at [openweathermap.org](https://openweathermap.org)
   - Get API key
   - Add to configuration

2. **Configure System**
   ```env
   WEATHER_API_KEY=your_weather_api_key
   WEATHER_API_URL=https://api.openweathermap.org/data/2.5/weather
   ```

---

## Security Configuration

### SSL/TLS Setup

**Using Let's Encrypt:**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

**Manual SSL Certificate:**

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
}
```

### Firewall Configuration

**UFW (Ubuntu):**

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow application port (if not using reverse proxy)
sudo ufw allow 5000

# Check status
sudo ufw status
```

**iptables:**

```bash
# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

---

## Monitoring and Maintenance

### System Monitoring

**Using systemd (Linux):**

```ini
# /etc/systemd/system/clinic-ai.service
[Unit]
Description=AI-Enhanced Booking Optimization
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
ExecStart=/path/to/your/app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable clinic-ai

# Start service
sudo systemctl start clinic-ai

# Check status
sudo systemctl status clinic-ai
```

### Log Management

**Log Rotation:**

```bash
# /etc/logrotate.d/clinic-ai
/path/to/your/app/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload clinic-ai
    endscript
}
```

### Backup Strategy

**Database Backup:**

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
DB_NAME="clinic_booking"

# Create backup
pg_dump $DB_NAME > $BACKUP_DIR/clinic_booking_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/clinic_booking_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "clinic_booking_*.sql.gz" -mtime +30 -delete
```

**Automated Backup:**

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

---

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 PID

# Or use different port
python app.py --port 5001
```

**Database Connection Error:**
```bash
# Check database file permissions
ls -la clinic_booking.db

# Fix permissions
chmod 664 clinic_booking.db
chown www-data:www-data clinic_booking.db
```

**Import Errors:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

**Permission Denied:**
```bash
# Check file permissions
ls -la

# Fix permissions
chmod +x app.py
chown -R www-data:www-data /path/to/your/app
```

### Performance Optimization

**Database Optimization:**

```sql
-- Add indexes for better performance
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_time ON appointments(appointment_time);
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_time);
```

**Application Optimization:**

```python
# In app.py, add caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/analytics/dashboard-stats')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_dashboard_stats():
    # ... existing code
```

---

## Support and Resources

### Documentation
- **User Guide**: `docs/training_guide.md`
- **Privacy Assessment**: `docs/privacy_impact_assessment.md`
- **API Documentation**: `docs/api_reference.md`

### Community Support
- **GitHub Issues**: [Repository Issues](https://github.com/your-org/ai-booking-optimization/issues)
- **Discussion Forum**: [Community Forum](https://github.com/your-org/ai-booking-optimization/discussions)
- **Email Support**: support@clinic-ai.com

### Professional Services
- **Installation Support**: installation@clinic-ai.com
- **Custom Development**: development@clinic-ai.com
- **Training Services**: training@clinic-ai.com

---

*This installation guide is regularly updated. Please check for the latest version and provide feedback for improvements.*

