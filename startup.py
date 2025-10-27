#!/usr/bin/env python3
"""
AI-Enhanced Booking Optimization System
Startup Script with Health Checks
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('startup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'pandas', 'scikit_learn',
        'twilio', 'sendgrid', 'cryptography'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Run: pip install -r requirements.txt")
        return False
    
    logger.info("All required packages are installed")
    return True

def check_environment():
    """Check environment configuration"""
    required_env_vars = ['SECRET_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.info("Please configure your .env file")
        return False
    
    logger.info("Environment configuration is valid")
    return True

def check_database():
    """Check database connectivity"""
    try:
        from app import db, app
        with app.app_context():
            # Try to execute a simple query
            db.session.execute('SELECT 1')
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def initialize_database():
    """Initialize database if needed"""
    try:
        from app import db, app
        with app.app_context():
            db.create_all()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def check_external_services():
    """Check external service configurations"""
    services_status = {}
    
    # Check Twilio configuration
    if os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN'):
        services_status['Twilio'] = 'Configured'
    else:
        services_status['Twilio'] = 'Not configured (optional)'
    
    # Check SendGrid configuration
    if os.getenv('SENDGRID_API_KEY'):
        services_status['SendGrid'] = 'Configured'
    else:
        services_status['SendGrid'] = 'Not configured (optional)'
    
    logger.info("External services status:")
    for service, status in services_status.items():
        logger.info(f"  {service}: {status}")
    
    return True

def run_health_checks():
    """Run comprehensive health checks"""
    logger.info("Starting health checks...")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Database", check_database),
        ("External Services", check_external_services)
    ]
    
    failed_checks = []
    for check_name, check_func in checks:
        logger.info(f"Running {check_name} check...")
        if not check_func():
            failed_checks.append(check_name)
    
    if failed_checks:
        logger.error(f"Health checks failed: {', '.join(failed_checks)}")
        return False
    
    logger.info("All health checks passed!")
    return True

def start_application():
    """Start the Flask application"""
    try:
        logger.info("Starting AI-Enhanced Booking Optimization System...")
        
        # Import and run the app
        from app import app
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('FLASK_ENV') == 'development'
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        return False
    
    return True

def main():
    """Main startup function"""
    logger.info("=" * 60)
    logger.info("AI-Enhanced Booking Optimization System")
    logger.info("Startup Script")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("=" * 60)
    
    # Run health checks
    if not run_health_checks():
        logger.error("Health checks failed. Please fix the issues above.")
        sys.exit(1)
    
    # Initialize database if needed
    if not initialize_database():
        logger.error("Database initialization failed.")
        sys.exit(1)
    
    # Start the application
    logger.info("Starting application...")
    start_application()

if __name__ == '__main__':
    main()

