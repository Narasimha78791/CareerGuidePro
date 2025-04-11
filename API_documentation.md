# API Documentation for Career Recommendation System

## Overview
The Career Recommendation System provides a set of API endpoints for accessing its features programmatically. These endpoints allow you to create and manage user profiles, get career recommendations, and access market trend data.

## Authentication
All API endpoints require authentication. Users must be logged in to access the API endpoints. The system uses session-based authentication through Flask-Login.

## API Endpoints

### User Profile Management

#### GET `/api/profile`
Retrieves the current user's profile information.

**Response Example:**
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "skills": "Python, JavaScript, Data Analysis",
  "interests": "Machine Learning, Web Development",
  "education": "Bachelor's in Computer Science",
  "experience": "5 years as a Software Developer"
}
```

#### PUT `/api/profile`
Updates the current user's profile information.

**Request Body Example:**
```json
{
  "name": "John Doe",
  "skills": "Python, JavaScript, Data Analysis, SQL",
  "interests": "Machine Learning, Web Development, Cloud Computing",
  "education": "Bachelor's in Computer Science, AWS Certification",
  "experience": "5 years as a Software Developer"
}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

### Career Recommendations

#### GET `/api/recommendations`
Retrieves career recommendations for the current user.

**Query Parameters:**
- `limit` (optional): Maximum number of recommendations to return (default: 5)

**Response Example:**
```json
{
  "recommendations": [
    {
      "career_id": 12,
      "name": "Data Scientist",
      "description": "Analyzes and interprets complex data to help guide business decisions",
      "required_skills": "Python, R, Statistics, Machine Learning",
      "industry": "Technology",
      "score": 0.85
    },
    {
      "career_id": 7,
      "name": "Full Stack Developer",
      "description": "Creates both client and server software for web applications",
      "required_skills": "JavaScript, HTML, CSS, Python, SQL",
      "industry": "Software Development",
      "score": 0.78
    }
  ]
}
```

#### GET `/api/careers/:id`
Retrieves detailed information about a specific career.

**Response Example:**
```json
{
  "career_id": 12,
  "name": "Data Scientist",
  "description": "Analyzes and interprets complex data to help guide business decisions",
  "required_skills": "Python, R, Statistics, Machine Learning",
  "industry": "Technology",
  "market_trends": {
    "demand_level": 0.9,
    "salary_range_min": 90000,
    "salary_range_max": 150000,
    "updated_at": "2025-03-15T12:30:45Z"
  }
}
```

### Skill Extraction

#### POST `/api/extract-skills`
Extracts skills from a provided text.

**Request Body Example:**
```json
{
  "text": "I have 5 years of experience with Python development and machine learning, particularly with TensorFlow and scikit-learn. I've worked on several data visualization projects using Matplotlib and Tableau."
}
```

**Response Example:**
```json
{
  "skills": [
    "Python",
    "machine learning",
    "TensorFlow",
    "scikit-learn",
    "data visualization",
    "Matplotlib",
    "Tableau"
  ]
}
```

### Market Trends

#### GET `/api/market-trends`
Retrieves market trend data for all careers or filtered by industry.

**Query Parameters:**
- `industry` (optional): Filter trends by industry

**Response Example:**
```json
{
  "trends": [
    {
      "career_id": 12,
      "career_name": "Data Scientist",
      "industry": "Technology",
      "demand_level": 0.9,
      "salary_range_min": 90000,
      "salary_range_max": 150000
    },
    {
      "career_id": 7,
      "career_name": "Full Stack Developer",
      "industry": "Software Development",
      "demand_level": 0.85,
      "salary_range_min": 80000,
      "salary_range_max": 140000
    }
  ]
}
```

## Error Handling
All API endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad request (invalid parameters)
- 401: Unauthorized (not logged in)
- 404: Resource not found
- 500: Server error

Error responses include a JSON body with an error message:
```json
{
  "error": "Error message description"
}
```

## Rate Limiting
API requests are limited to 100 requests per hour per user to prevent abuse.