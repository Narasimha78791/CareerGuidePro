# Career Recommendation System - ML Data Sources

## Overview
This document outlines the data sources, schema, and preprocessing techniques used in the machine learning components of the career recommendation system.

## Primary Data Sources

### Career Information
The system's career data is sourced from the following:

1. **Careers Database Table**: Structured information including:
   - Career titles
   - Descriptions
   - Required skills
   - Industry classifications

2. **Static Data Files**: 
   - `static/data/careers.json`: Contains core career definitions
   - `static/data/market_trends.json`: Contains salary and demand information

### User Profile Data
User information is collected from:

1. **User Database Table**: Contains:
   - Basic profile information
   - Self-reported skills
   - Educational background
   - Experience summary
   - Career interests

2. **Feedback Data**: 
   - User ratings of recommendations
   - Comments and feedback on career suggestions
   - Indicates which recommendations were most helpful

## Data Schema

### Career Data Schema
```json
{
  "id": 1,
  "name": "Data Scientist",
  "description": "Detailed description of the career...",
  "required_skills": "Python, R, Statistics, Machine Learning, Data Visualization",
  "industry": "Technology",
  "market_trends": {
    "demand_level": 0.85,
    "salary_range_min": 90000,
    "salary_range_max": 150000
  }
}
```

### User Profile Schema
```json
{
  "id": 1,
  "name": "User Name",
  "skills": "Python, JavaScript, Data Analysis",
  "education": "Bachelor's in Computer Science",
  "experience": "5 years as a Software Developer",
  "interests": "Machine Learning, Web Development"
}
```

## Data Preprocessing

### Text Preprocessing
- **Tokenization**: Text fields are split into tokens using NLTK
- **Stopword Removal**: Common words are filtered out
- **Normalization**: Terms are converted to lowercase
- **Stemming/Lemmatization**: Words are reduced to their root forms

### Feature Engineering
- **TF-IDF Vectorization**: Creates numerical representations of text
- **Skill Classification**: Categorizes skills into technical domains
- **Industry Normalization**: Maps varied industry terms to standard categories
- **Education Level Extraction**: Identifies degree levels and fields of study

### Data Quality Assurance
- **Duplicate Detection**: Identifies and removes duplicate entries
- **Missing Value Handling**: Strategies for dealing with incomplete profiles
- **Outlier Detection**: Identifies unusual skill combinations or career paths

## Data Update Mechanisms

### Career Data Updates
- Market trend data is updated monthly to reflect current job market conditions
- New careers are added to the database as they emerge
- Skill requirements are refreshed to match evolving job descriptions

### User Data Processing
- User profiles are processed in real-time when recommendations are requested
- Feedback is incorporated into the system weekly to improve recommendations
- Historical recommendation data is archived for model training

## Data Privacy and Security
- All user data is processed according to privacy guidelines
- Personal identifiers are separated from ML training data
- Data is encrypted both in transit and at rest
- User consent is required for all data collection and processing