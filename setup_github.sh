#!/bin/bash
# GitHub Repository Setup Script for BRUKD Consultancy AI Booking System

echo "Setting up GitHub repository for BRUKD Consultancy AI Booking Optimization System..."

# Initialize Git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: BRUKD Consultancy AI-Enhanced Booking Optimization System

- Complete Flask application with AI no-show prediction
- Automated reminder system (SMS, email, chat)
- PIPEDA-compliant privacy features
- Realistic sample data for demonstration
- BRUKD-branded dashboard interface
- Comprehensive documentation and training materials"

# Add remote origin (you'll need to create the repository on GitHub first)
echo "Please create a new repository on GitHub named 'ai-booking-optimization' under your account"
echo "Then run: git remote add origin https://github.com/YOUR_USERNAME/ai-booking-optimization.git"
echo "And: git push -u origin main"

# Create .gitignore file
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Machine Learning Models
models/*.pkl
models/*.joblib
*.model

# Instance folder
instance/

# Flask
.flaskenv

# Testing
.coverage
.pytest_cache/
htmlcov/

# Backup files
*.bak
*.backup
*.tmp
EOF

# Add .gitignore
git add .gitignore
git commit -m "Add .gitignore file"

echo "Git repository initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub named 'ai-booking-optimization'"
echo "2. Add the remote origin: git remote add origin https://github.com/YOUR_USERNAME/ai-booking-optimization.git"
echo "3. Push to GitHub: git push -u origin main"
echo ""
echo "Your BRUKD Consultancy AI Booking System is ready for GitHub!"
