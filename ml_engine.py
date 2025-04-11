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
        # Load common IT/programming terms to improve matching
        self.tech_skills = [
            "python", "java", "javascript", "html", "css", "sql", "nosql", "react", 
            "angular", "vue", "node", "express", "django", "flask", "spring", 
            "machine learning", "data science", "data analysis", "artificial intelligence",
            "cloud", "aws", "azure", "gcp", "devops", "ci/cd", "docker", "kubernetes",
            "design", "photoshop", "illustrator", "ui", "ux", "wireframing", "prototyping"
        ]
        
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
        
        # Get user skills and interests as separate lists for direct matching
        user_skills = self._extract_keywords(user_profile.get('skills', ''))
        user_interests = self._extract_keywords(user_profile.get('interests', ''))
        user_education = self._extract_keywords(user_profile.get('education', ''))
        user_experience = self._extract_keywords(user_profile.get('experience', ''))
        
        logging.debug(f"User skills: {user_skills}")
        logging.debug(f"User interests: {user_interests}")
        
        # Calculate direct skill match scores
        direct_match_scores = []
        for idx, career in enumerate(self.careers_data):
            career_skills = self._extract_keywords(career['required_skills'])
            career_desc = self._extract_keywords(career['description'])
            career_industry = self._extract_keywords(career['industry'])
            
            # Calculate direct skill matches
            skill_matches = sum(1 for skill in user_skills if any(self._keyword_match(skill, cs) for cs in career_skills))
            interest_matches = sum(1 for interest in user_interests if any(self._keyword_match(interest, cd) for cd in career_desc + career_industry))
            
            # Normalize by the max possible matches and weight skills higher
            skill_match_score = skill_matches / max(len(user_skills), 1) * 0.7 if user_skills else 0
            interest_match_score = interest_matches / max(len(user_interests), 1) * 0.3 if user_interests else 0
            
            # Combined score
            direct_score = skill_match_score + interest_match_score
            direct_match_scores.append(direct_score)
            
        # Use vectorizer for semantic similarity as well
        user_text = self._preprocess_user_profile(user_profile)
        try:
            user_features = self.vectorizer.transform([user_text])
            semantic_similarities = cosine_similarity(user_features, self.career_features).flatten()
            
            # Combine direct matching with semantic similarity
            # Weight: 60% direct matching, 40% semantic similarity
            combined_scores = [0.6 * direct + 0.4 * semantic for direct, semantic in zip(direct_match_scores, semantic_similarities)]
            
            logging.debug(f"Combined scores range: {min(combined_scores):.4f} to {max(combined_scores):.4f}")
        except Exception as e:
            logging.error(f"Error calculating semantic similarity: {str(e)}")
            # Fall back to just direct matching if vectorizer fails
            combined_scores = direct_match_scores
            
        # Get indices of top recommendations
        top_indices = np.array(combined_scores).argsort()[-num_recommendations:][::-1]
        
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
                'score': float(combined_scores[idx]),  # Convert numpy float to Python float
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
    
    def _extract_keywords(self, text):
        """Extract keywords from text, removing stopwords and normalizing"""
        if not text:
            return []
            
        # Convert to lowercase and tokenize by splitting on commas and spaces
        keywords = []
        for token in text.lower().replace(',', ' ').split():
            # Filter out stopwords and short words
            if len(token) > 2 and token not in stopwords.words('english'):
                keywords.append(token)
                
        # Return unique keywords
        return list(set(keywords))
    
    def _keyword_match(self, user_keyword, career_keyword):
        """Check if a user keyword matches a career keyword
        Handles partial matches and common variations"""
        # Exact match
        if user_keyword == career_keyword:
            return True
            
        # One is substring of the other (case insensitive)
        if user_keyword in career_keyword or career_keyword in user_keyword:
            return True
            
        # Special case for tech skills (exact match only)
        if user_keyword.lower() in self.tech_skills and career_keyword.lower() in self.tech_skills:
            return user_keyword.lower() == career_keyword.lower()
            
        # Substring match but need at least 4 characters to match
        if len(user_keyword) >= 4 and len(career_keyword) >= 4:
            if user_keyword[:4] in career_keyword or career_keyword[:4] in user_keyword:
                return True
                
        return False
    
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
