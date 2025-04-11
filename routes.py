from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Career, Recommendation, Feedback, MarketTrend, MLModel
from ml_engine import CareerRecommendationEngine
from werkzeug.security import generate_password_hash, check_password_hash
import json
import logging
from datetime import datetime
import os

# Initialize the ML engine
ml_engine = CareerRecommendationEngine()

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('register.html')
            
        # Create new user
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error during registration: {str(e)}")
            flash('An error occurred during registration', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('profile'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile route"""
    # Get user's recommendations
    recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(Recommendation.created_at.desc()).limit(5).all()
    return render_template('profile.html', user=current_user, recommendations=recommendations)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile route"""
    if request.method == 'POST':
        # Update user information
        current_user.name = request.form.get('name')
        current_user.age = request.form.get('age')
        current_user.skills = request.form.get('skills')
        current_user.education = request.form.get('education')
        current_user.experience = request.form.get('experience')
        current_user.interests = request.form.get('interests')
        
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating profile: {str(e)}")
            flash('An error occurred while updating your profile', 'danger')
    
    return render_template('edit_profile.html', user=current_user)

@app.route('/get-recommendations')
@login_required
def get_recommendations():
    """Generate career recommendations for the user"""
    # Check if user has provided necessary information
    if not current_user.skills and not current_user.education and not current_user.interests:
        flash('Please complete your profile to get recommendations', 'warning')
        return redirect(url_for('edit_profile'))
    
    # Prepare user profile for the ML engine
    user_profile = {
        'skills': current_user.skills or '',
        'education': current_user.education or '',
        'experience': current_user.experience or '',
        'interests': current_user.interests or ''
    }
    
    try:
        # First, delete all existing recommendations for this user
        # This ensures we don't have duplicates or old recommendations
        existing_recommendations = Recommendation.query.filter_by(user_id=current_user.id).all()
        
        # Remove any associated feedback first (to avoid foreign key constraint errors)
        for rec in existing_recommendations:
            Feedback.query.filter_by(recommendation_id=rec.id).delete()
        
        # Now delete the recommendations
        Recommendation.query.filter_by(user_id=current_user.id).delete()
        
        # Get recommendations from ML engine
        recommendations = ml_engine.get_recommendations(user_profile)
        
        # Create a set to track career IDs we've already added
        # This provides an extra layer of deduplication
        added_career_ids = set()
        
        # Store recommendations in the database
        for rec in recommendations:
            # Skip if we already added this career (prevents duplicates)
            if rec['career_id'] in added_career_ids:
                continue
                
            # Add to our tracking set
            added_career_ids.add(rec['career_id'])
            
            # Check if career exists in the database, if not create it
            career = Career.query.filter_by(id=rec['career_id']).first()
            if not career:
                career = Career(
                    id=rec['career_id'],
                    name=rec['name'],
                    description=rec['description'],
                    required_skills=rec['required_skills'],
                    industry=rec['industry']
                )
                db.session.add(career)
            
            # Create recommendation
            new_recommendation = Recommendation(
                user_id=current_user.id,
                career_id=career.id,
                score=rec['score']
            )
            db.session.add(new_recommendation)
        
        db.session.commit()
        flash('Your career recommendations have been updated', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error generating recommendations: {str(e)}")
        flash('An error occurred while processing your recommendations', 'danger')
        return redirect(url_for('profile'))
    
    return redirect(url_for('recommendations'))

@app.route('/recommendations')
@login_required
def recommendations():
    """View career recommendations"""
    user_recommendations = Recommendation.query.filter_by(user_id=current_user.id).order_by(Recommendation.score.desc()).all()
    
    return render_template('recommendations.html', recommendations=user_recommendations)

@app.route('/career/<int:career_id>')
@login_required
def career_details(career_id):
    """View details of a specific career"""
    career = Career.query.get_or_404(career_id)
    market_trend = MarketTrend.query.filter_by(career_id=career_id).first()
    
    # If market trend doesn't exist in database, try to get it from JSON data
    if not market_trend:
        try:
            with open('static/data/market_trends.json', 'r') as f:
                trends_data = json.load(f)
                for trend in trends_data:
                    if trend.get('career_id') == career_id:
                        # Create market trend in the database
                        market_trend = MarketTrend(
                            career_id=career_id,
                            demand_level=trend.get('demand_level', 0.5),
                            salary_range_min=trend.get('salary_range_min', 30000),
                            salary_range_max=trend.get('salary_range_max', 80000)
                        )
                        try:
                            db.session.add(market_trend)
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            logging.error(f"Error creating market trend: {str(e)}")
        except FileNotFoundError:
            logging.warning("Market trends data file not found")
            # Create a default market trend
            market_trend = MarketTrend(
                career_id=career_id,
                demand_level=0.5,  # Medium demand
                salary_range_min=40000,
                salary_range_max=90000
            )
    
    # Get the recommendation for this career (if exists)
    recommendation = Recommendation.query.filter_by(user_id=current_user.id, career_id=career_id).first()
    
    return render_template('career_details.html', career=career, market_trend=market_trend, recommendation=recommendation)

@app.route('/feedback/<int:recommendation_id>', methods=['GET', 'POST'])
@login_required
def feedback(recommendation_id):
    """Provide feedback for a recommendation"""
    recommendation = Recommendation.query.get_or_404(recommendation_id)
    
    # Ensure the recommendation belongs to the current user
    if recommendation.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('recommendations'))
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comments = request.form.get('comments')
        
        # Validation
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (TypeError, ValueError):
            flash('Please provide a valid rating (1-5)', 'danger')
            return redirect(url_for('feedback', recommendation_id=recommendation_id))
        
        # Check for existing feedback
        existing_feedback = Feedback.query.filter_by(user_id=current_user.id, recommendation_id=recommendation_id).first()
        
        if existing_feedback:
            # Update existing feedback
            existing_feedback.rating = rating
            existing_feedback.comments = comments
        else:
            # Create new feedback
            new_feedback = Feedback(
                user_id=current_user.id,
                recommendation_id=recommendation_id,
                rating=rating,
                comments=comments
            )
            db.session.add(new_feedback)
        
        try:
            db.session.commit()
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('recommendations'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error saving feedback: {str(e)}")
            flash('An error occurred while saving your feedback', 'danger')
    
    # Check if user has already provided feedback
    existing_feedback = Feedback.query.filter_by(user_id=current_user.id, recommendation_id=recommendation_id).first()
    
    return render_template('feedback.html', recommendation=recommendation, existing_feedback=existing_feedback)

@app.route('/market-trends')
@login_required
def market_trends():
    """View market trends for different careers"""
    # Get all careers with their market trends
    careers_with_trends = db.session.query(Career, MarketTrend).join(
        MarketTrend, Career.id == MarketTrend.career_id, isouter=True
    ).all()
    
    return render_template('market_trends.html', careers_with_trends=careers_with_trends)

@app.route('/api/extract-skills', methods=['POST'])
@login_required
def extract_skills():
    """API endpoint to extract skills from text"""
    data = request.get_json()
    text = data.get('text', '')
    
    skills = ml_engine.extract_skills_from_text(text)
    
    return jsonify({'skills': skills})

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
