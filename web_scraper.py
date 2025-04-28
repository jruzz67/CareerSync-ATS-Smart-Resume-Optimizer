import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_job_description(job_title, user_job_description):
    if user_job_description:
        logger.debug("Using user-provided job description")
        return user_job_description
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        # Try LinkedIn
        url = f"https://www.linkedin.com/jobs/search?keywords={job_title.replace(' ', '%20')}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        job_desc = ""
        # Broader selector
        for job in soup.find_all(['div', 'section'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['description', 'job', 'posting', 'details'])):
            text = job.get_text(strip=True)
            if text:
                job_desc += text + " "
            if len(job_desc) > 500:
                break
        
        if not job_desc:
            # Fallback to Indeed
            url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for job in soup.find_all(['div', 'section'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['description', 'job', 'posting'])):
                text = job.get_text(strip=True)
                if text:
                    job_desc += text + " "
                if len(job_desc) > 500:
                    break
        
        if not job_desc:
            raise ValueError("No job descriptions found")
        
        logger.debug(f"Scraped job description: {job_desc[:100]}...")
        return job_desc.strip()
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        logger.warning("Using default job description due to scraping failure")
        return f"Job description for {job_title}: Seeking a professional with relevant skills and experience."