import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
import os
import logging
from datetime import datetime

# Download NLTK resources if not already present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class CareerRecommendationEngine:
    def __init__(self):
        self.careers_data = self._load_careers_data()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.career_features = None
        self._preprocess_careers()
        
    def _load_careers_data(self):
        """Load career data from JSON file or database"""
        try:
            # Attempt to load from the static data file
            with open('static/data/careers.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to a minimal dataset if file not found
            logging.warning("Careers data file not found. Using minimal dataset.")
            return self._get_fallback_careers_data()
    
    def _get_fallback_careers_data(self):
        """Provide a minimal careers dataset as fallback"""
        return [
            {
                "id": 1,
                "name": "Software Developer",
                "description": "Develops software applications by designing, coding, and testing.",
                "required_skills": "Python, JavaScript, Database Management, Problem Solving",
                "industry": "Information Technology"
            },
            {
                "id": 2,
                "name": "Data Scientist",
                "description": "Analyzes and interprets complex data to help organizations make better decisions.",
                "required_skills": "Python, R, Machine Learning, Statistics, Data Visualization",
                "industry": "Information Technology"
            },
            {
                "id": 3,
                "name": "Marketing Manager",
                "description": "Develops and implements marketing strategies to promote products or services.",
                "required_skills": "Communication, Marketing, Social Media, Strategic Planning",
                "industry": "Marketing"
            },
            {
                "id": 4,
                "name": "Financial Analyst",
                "description": "Analyzes financial data and provides insights for business decisions.",
                "required_skills": "Financial Modeling, Excel, Data Analysis, Accounting",
                "industry": "Finance"
            },
            {
                "id": 5,
                "name": "Human Resources Manager",
                "description": "Manages HR functions including recruitment, employee relations, and training.",
                "required_skills": "Communication, Conflict Resolution, Employee Relations, Recruitment",
                "industry": "Human Resources"
            }
        ]
    
    def _preprocess_careers(self):
        """Preprocess career data to create feature vectors"""
        career_texts = []
        for career in self.careers_data:
            # Combine relevant fields for better matching
            combined_text = f"{career['name']} {career['description']} {career['required_skills']} {career['industry']}"
            career_texts.append(combined_text.lower())
        
        # Create TF-IDF features
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
        self.career_features = self.vectorizer.fit_transform(career_texts)
    
    def _preprocess_user_profile(self, user_profile):
        """Preprocess user profile for recommendation"""
        # Give higher weight to skills and interests
        skills = user_profile.get('skills', '').strip()
        interests = user_profile.get('interests', '').strip()
        education = user_profile.get('education', '').strip()
        experience = user_profile.get('experience', '').strip()
        
        # Give more weight to skills and interests by repeating them
        weighted_text = f"{skills} {skills} {skills} {interests} {interests} {education} {experience}"
        return weighted_text.lower()
    
    def get_recommendations(self, user_profile, num_recommendations=5):
        """Generate career recommendations based on user profile"""
        # Check if user profile has sufficient data
        if not user_profile.get('skills') and not user_profile.get('interests'):
            logging.warning("User profile lacks sufficient data for accurate recommendations")
            # Return diverse recommendations from different industries
            return self._get_diverse_recommendations(num_recommendations)
            
        # Preprocess user profile
        user_text = self._preprocess_user_profile(user_profile)
        logging.debug(f"Processed user profile text: {user_text}")
        
        # Transform user text using the same vectorizer
        try:
            user_features = self.vectorizer.transform([user_text])
            
            # Calculate similarity between user profile and each career
            similarities = cosine_similarity(user_features, self.career_features).flatten()
            logging.debug(f"Similarity scores range: {similarities.min():.4f} to {similarities.max():.4f}")
        except Exception as e:
            logging.error(f"Error calculating recommendations: {str(e)}")
            return self._get_diverse_recommendations(num_recommendations)
        
        # Get indices of top recommendations
        top_indices = similarities.argsort()[-num_recommendations:][::-1]
        
        # Create recommendation results
        recommendations = []
        for idx in top_indices:
            career = self.careers_data[idx]
            recommendations.append({
                'career_id': career['id'],
                'name': career['name'],
                'description': career['description'],
                'required_skills': career['required_skills'],
                'industry': career['industry'],
                'score': float(similarities[idx]),  # Convert numpy float to Python float
                'timestamp': datetime.now().isoformat()
            })
        
        return recommendations
    
    def get_career_by_id(self, career_id):
        """Retrieve a career by its ID"""
        for career in self.careers_data:
            if career['id'] == career_id:
                return career
        return None
    
    def get_all_careers(self):
        """Return all careers data"""
        return self.careers_data
        
    def _get_diverse_recommendations(self, num_recommendations=5):
        """Return diverse career recommendations from different industries"""
        # Get unique industries
        industries = {}
        for career in self.careers_data:
            industry = career['industry']
            if industry not in industries:
                industries[industry] = []
            industries[industry].append(career)
        
        # Select careers from different industries
        recommendations = []
        industries_list = list(industries.keys())
        
        # Ensure we don't try to get more recommendations than available industries
        num_industries = min(num_recommendations, len(industries_list))
        
        for i in range(num_industries):
            industry = industries_list[i % len(industries_list)]
            # Get a career from this industry that we haven't recommended yet
            industry_careers = industries[industry]
            for career in industry_careers:
                # Check if we've already recommended this career
                if not any(rec.get('career_id') == career['id'] for rec in recommendations):
                    recommendations.append({
                        'career_id': career['id'],
                        'name': career['name'],
                        'description': career['description'],
                        'required_skills': career['required_skills'],
                        'industry': career['industry'],
                        'score': 0.6,  # Medium score for default recommendations
                        'timestamp': datetime.now().isoformat()
                    })
                    break
            
            # If we have enough recommendations, stop
            if len(recommendations) >= num_recommendations:
                break
                
        return recommendations
    
    def extract_skills_from_text(self, text):
        """Extract potential skills from a text input"""
        if not text:
            return []
            
        # Tokenize and filter tokens
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
        
        # Count frequency
        freq = pd.Series(tokens).value_counts()
        
        # Return top skills (tokens that appear more than once)
        return freq[freq > 1].index.tolist()
