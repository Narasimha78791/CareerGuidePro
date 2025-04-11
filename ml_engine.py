import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
import os
import logging
import re
from datetime import datetime

# Setup better logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
        # Load common skills across different domains to improve matching
        self.tech_skills = [
            # Technical/IT Skills
            "python", "java", "javascript", "typescript", "html", "css", "sql", "nosql", "react", 
            "angular", "vue", "node", "express", "django", "flask", "spring", "ruby", "php", "c++", "c#",
            "machine learning", "data science", "data analysis", "artificial intelligence", "nlp",
            "cloud", "aws", "azure", "gcp", "devops", "ci/cd", "docker", "kubernetes", "jenkins",
            "blockchain", "ethereum", "solidity", "cybersecurity", "networking", "linux", "unix",
            
            # Design Skills
            "design", "photoshop", "illustrator", "figma", "sketch", "indesign", "ui", "ux", 
            "wireframing", "prototyping", "typography", "color theory", "graphic design",
            
            # Business/Management Skills
            "project management", "agile", "scrum", "marketing", "sales", "seo", "social media",
            "analytics", "leadership", "communication", "teamwork", "finance", "accounting",
            "business analysis", "strategy", "operations", "human resources", "consulting",
            
            # Healthcare/Science Skills
            "medicine", "biology", "chemistry", "physics", "research", "healthcare", "patient care",
            "clinical", "laboratory", "pharmaceutical", "nursing", "therapy", "diagnostic",
            
            # Creative/Media Skills
            "writing", "editing", "content creation", "journalism", "copywriting", "video editing",
            "animation", "photography", "storytelling", "audio production", "music", "filmmaking"
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
        """Generate career recommendations based on user profile using a sophisticated matching algorithm"""
        # Check if user profile has sufficient data
        if not user_profile.get('skills') and not user_profile.get('interests'):
            logging.warning("User profile lacks sufficient data for accurate recommendations")
            # Return diverse recommendations from different industries
            return self._get_diverse_recommendations(num_recommendations)
        
        # Extract user skills and interests as separate lists for direct matching
        user_skills = self._extract_keywords(user_profile.get('skills', ''))
        user_interests = self._extract_keywords(user_profile.get('interests', ''))
        user_education = self._extract_keywords(user_profile.get('education', ''))
        user_experience = self._extract_keywords(user_profile.get('experience', ''))
        
        logging.debug(f"User skills: {user_skills}")
        logging.debug(f"User interests: {user_interests}")
        
        # Initialize scores for each matching method
        skill_match_scores = []
        interest_match_scores = []
        education_match_scores = []
        experience_match_scores = []
        semantic_match_scores = []
        
        # Calculate detailed match scores for each career
        for idx, career in enumerate(self.careers_data):
            # Extract career keywords
            career_skills = self._extract_keywords(career['required_skills'])
            career_desc = self._extract_keywords(career['description'])
            career_industry = self._extract_keywords(career['industry'])
            career_name_keywords = self._extract_keywords(career['name'])
            
            # Combined career keywords for better matching
            all_career_keywords = career_skills + career_desc + career_industry + career_name_keywords
            
            # 1. Skill matching with detailed scoring
            skill_score = 0
            if user_skills:
                # Count exact matches (higher weight)
                exact_matches = sum(1 for skill in user_skills if any(skill.lower() == cs.lower() for cs in career_skills))
                # Count partial matches (lower weight)
                partial_matches = sum(1 for skill in user_skills if any(self._keyword_match(skill, cs) for cs in career_skills) and 
                                     not any(skill.lower() == cs.lower() for cs in career_skills))
                
                # Calculate weighted score (exact matches count more)
                skill_score = (exact_matches * 1.5 + partial_matches * 0.5) / max(len(user_skills), 1)
                
                # Bonus for high skill coverage
                if len(user_skills) > 2 and exact_matches >= len(user_skills) * 0.5:
                    skill_score *= 1.2  # 20% boost for having many relevant skills
            
            # 2. Interest matching (check against description and industry)
            interest_score = 0
            if user_interests:
                interest_matches = sum(1 for interest in user_interests if any(self._keyword_match(interest, kw) for kw in career_desc + career_industry))
                interest_score = interest_matches / max(len(user_interests), 1)
            
            # 3. Education matching
            education_score = 0
            if user_education:
                edu_matches = sum(1 for edu in user_education if any(self._keyword_match(edu, kw) for kw in all_career_keywords))
                education_score = edu_matches / max(len(user_education), 1) * 0.8  # Slightly less weight
            
            # 4. Experience matching
            experience_score = 0
            if user_experience:
                exp_matches = sum(1 for exp in user_experience if any(self._keyword_match(exp, kw) for kw in all_career_keywords))
                experience_score = exp_matches / max(len(user_experience), 1) * 0.8
            
            # Store individual scores
            skill_match_scores.append(skill_score)
            interest_match_scores.append(interest_score)
            education_match_scores.append(education_score)
            experience_match_scores.append(experience_score)
        
        # 5. Calculate semantic similarity using TF-IDF vectorization
        user_text = self._preprocess_user_profile(user_profile)
        try:
            user_features = self.vectorizer.transform([user_text])
            semantic_similarities = cosine_similarity(user_features, self.career_features).flatten()
            semantic_match_scores = list(semantic_similarities)
        except Exception as e:
            logging.error(f"Error calculating semantic similarity: {str(e)}")
            semantic_match_scores = [0.3] * len(self.careers_data)  # Fallback
        
        # 6. Combine all scores with appropriate weights
        combined_scores = []
        for i in range(len(self.careers_data)):
            # Weighted average of all scores - skills have highest weight
            score = (
                skill_match_scores[i] * 0.45 +          # Skills (highest weight)
                interest_match_scores[i] * 0.25 +        # Interests
                semantic_match_scores[i] * 0.15 +        # Semantic analysis
                education_match_scores[i] * 0.1 +        # Education
                experience_match_scores[i] * 0.05        # Experience
            )
            combined_scores.append(score)
        
        logging.debug(f"Combined scores range: {min(combined_scores):.4f} to {max(combined_scores):.4f}")
        
        # Ensure diversity by getting recommendations from different industries if possible
        # (if we have enough high scoring careers)
        top_indices = []
        all_indices = np.array(combined_scores).argsort()[::-1]  # All indices, sorted by score
        
        # First, add the highest scoring careers up to num_recommendations
        top_indices = list(all_indices[:num_recommendations])
        
        # Ensure we have careers from at least 3 different industries if possible
        seen_industries = set(self.careers_data[idx]['industry'] for idx in top_indices)
        if len(seen_industries) < min(3, len(set(career['industry'] for career in self.careers_data))):
            # Try to add more diverse industries by replacing lower scored careers
            for idx in all_indices[num_recommendations:num_recommendations+10]:  # Look at next 10 careers
                industry = self.careers_data[idx]['industry']
                if industry not in seen_industries:
                    # Replace the lowest scored career in our recommendations
                    lowest_score_idx = min(top_indices, key=lambda i: combined_scores[i])
                    lowest_score_industry = self.careers_data[lowest_score_idx]['industry']
                    
                    # Only replace if we have more than one career from this industry
                    if list(self.careers_data[i]['industry'] for i in top_indices).count(lowest_score_industry) > 1:
                        top_indices.remove(lowest_score_idx)
                        top_indices.append(idx)
                        seen_industries.add(industry)
                
                # Stop if we've reached desired industry diversity
                if len(seen_industries) >= 3:
                    break
        
        # Sort final recommendations by score
        top_indices.sort(key=lambda idx: combined_scores[idx], reverse=True)
        
        # Create recommendation results, ensuring no duplicates
        recommendations = []
        seen_names = set()  # Track career names to prevent duplicates
        
        # First pass: Add top scoring unique careers
        for idx in top_indices:
            career = self.careers_data[idx]
            if career['name'] not in seen_names:
                recommendations.append({
                    'career_id': career['id'],
                    'name': career['name'],
                    'description': career['description'],
                    'required_skills': career['required_skills'],
                    'industry': career['industry'],
                    'score': float(combined_scores[idx]),  # Convert numpy float to Python float
                    'timestamp': datetime.now().isoformat()
                })
                seen_names.add(career['name'])
        
        # Second pass: If we don't have enough recommendations due to duplicates,
        # find additional careers from other high-scoring options
        if len(recommendations) < num_recommendations:
            # Get more indices beyond what we originally selected
            extended_indices = np.array(combined_scores).argsort()[-(num_recommendations*3):][::-1]
            
            # Fill in with additional recommendations
            for idx in extended_indices:
                if len(recommendations) >= num_recommendations:
                    break
                    
                career = self.careers_data[idx]
                if career['name'] not in seen_names:
                    recommendations.append({
                        'career_id': career['id'],
                        'name': career['name'],
                        'description': career['description'],
                        'required_skills': career['required_skills'],
                        'industry': career['industry'],
                        'score': float(combined_scores[idx]),  # Convert numpy float to Python float
                        'timestamp': datetime.now().isoformat()
                    })
                    seen_names.add(career['name'])
        
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
        seen_career_names = set()  # Track career names to ensure no duplicates
        industries_list = list(industries.keys())
        
        # Shuffle industries to get different recommendations each time
        np.random.shuffle(industries_list)
        
        # Ensure we don't try to get more recommendations than available industries
        num_industries = min(num_recommendations, len(industries_list))
        
        for i in range(num_industries):
            industry = industries_list[i % len(industries_list)]
            # Shuffle careers within this industry to get different ones each time
            industry_careers = industries[industry].copy()
            np.random.shuffle(industry_careers)
            
            # Find a career from this industry that we haven't recommended yet
            added = False
            for career in industry_careers:
                # Check if career name is already in recommendations
                if career['name'] not in seen_career_names:
                    recommendations.append({
                        'career_id': career['id'],
                        'name': career['name'],
                        'description': career['description'],
                        'required_skills': career['required_skills'],
                        'industry': career['industry'],
                        'score': 0.6,  # Medium score for default recommendations
                        'timestamp': datetime.now().isoformat()
                    })
                    seen_career_names.add(career['name'])
                    added = True
                    break
            
            # If we couldn't add any career from this industry, try the next one
            if not added:
                continue
                
            # If we have enough recommendations, stop
            if len(recommendations) >= num_recommendations:
                break
                
        # If we still don't have enough recommendations, add careers from any industry
        if len(recommendations) < num_recommendations:
            all_careers = self.careers_data.copy()
            np.random.shuffle(all_careers)
            
            for career in all_careers:
                if career['name'] not in seen_career_names and len(recommendations) < num_recommendations:
                    recommendations.append({
                        'career_id': career['id'],
                        'name': career['name'],
                        'description': career['description'],
                        'required_skills': career['required_skills'],
                        'industry': career['industry'],
                        'score': 0.5,  # Slightly lower score for these fallback recommendations
                        'timestamp': datetime.now().isoformat()
                    })
                    seen_career_names.add(career['name'])
                    
            # If we still don't have enough, that means our dataset is too small
            if len(recommendations) < num_recommendations:
                logging.warning(f"Could only generate {len(recommendations)} recommendations from the available data")
                
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
