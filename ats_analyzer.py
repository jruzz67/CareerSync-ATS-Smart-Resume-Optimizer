import logging
import os
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing in environment variables.")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_resume_with_gemini(resume_text, job_description, job_title):
    if not resume_text or not job_description:
        logger.error("Resume text or job description missing")
        raise ValueError("Resume text and job description are required")
    
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Prompt for ATS analysis
        prompt = f"""
        You are an ATS (Applicant Tracking System) analyzer for a {job_title} role. 
        Analyze the resume and job description to calculate:
        - ATS compatibility út (0-100%)
        - Relevant skills
        - Keywords
        - Trending skills
        - Trending keywords
        - Suggestions for improvement
        
        Return the response strictly in JSON format:
        {{
            "ats_compatibility_score": int,
            "skills": [],
            "keywords": [],
            "trending_skills": [],
            "trending_keywords": [],
            "suggestions": []
        }}
        
        Resume: {resume_text}
        Job Description: {job_description}
        """

        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 1000,
                "temperature": 0.3
            }
        )
        
        # Extract and parse the result
        result_text = response.text.strip()
        try:
            # Remove markdown code block markers if present
            if result_text.startswith("```json") and result_text.endswith("```"):
                result_text = result_text[7:-3].strip()
            result = json.loads(result_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {str(e)}")
            raise ValueError(f"Gemini returned invalid JSON: {result_text}")
        
        logger.debug(f"ATS analysis result: {result}")
        return result

    except Exception as e:
        logger.error(f"Gemini error: {str(e)}")
        raise RuntimeError(f"Failed to analyze resume: {str(e)}")