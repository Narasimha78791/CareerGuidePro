# AI Career Recommendation System - Setup Guide

## Overview
This system uses machine learning techniques to recommend career paths based on a user's skills, interests, education, and experience. It provides personalized career recommendations with detailed information about each career path.

## Requirements
The system relies on the following packages:
- Flask and extensions (flask-login, flask-sqlalchemy)
- PostgreSQL database (with psycopg2-binary)
- Machine learning tools (numpy, pandas, scikit-learn, nltk)
- Web interface tools (gunicorn, werkzeug)

## Setup Instructions

### 1. Environment Setup
Make sure you have Python 3.11+ installed. All dependencies are managed automatically in the Replit environment.

### 2. Database Setup
The system uses PostgreSQL for data storage. To set up:
- Database tables are created automatically on first run
- Sample career data is loaded from static/data/careers.json
- Market trend data is loaded from static/data/market_trends.json

### 3. Running the Application
- The application runs on port 5000
- Start the application using the workflow "Start application"
- The server uses Gunicorn for better performance in production

### 4. Features
- User registration and login
- Profile creation with skills, interests, education, and experience
- AI-based career recommendations
- Visualization of career matches with interactive charts
- Market trend analysis for different career paths
- Skill extraction from text to help users identify their skills

## Project Structure
- `app.py` - Application initialization and configuration
- `main.py` - Entry point for the application
- `models.py` - Database models for users, careers, recommendations, etc.
- `ml_engine.py` - Machine learning engine for recommendations
- `routes.py` - Web routes and controllers
- `static/` - Static assets (CSS, JS, data files)
- `templates/` - HTML templates

## Machine Learning Details
The recommendation engine uses a multi-factor algorithm:
1. TF-IDF vectorization for semantic similarity
2. Direct keyword matching for skills and interests
3. Industry diversification to provide varied recommendations
4. Score weighting to prioritize important factors

## Security Considerations
- Passwords are hashed using werkzeug security functions
- PostgreSQL connections use environment variables for security
- User inputs are validated to prevent injection attacks