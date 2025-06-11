#!/usr/bin/env python3
"""
Enhanced JobTech Job Scraper for Swedish Jobs

This script uses the JobTech API (Arbetsförmedlingen) to search for IT, AI, and RPA jobs
in Gothenburg and Kungsbacka, with advanced contextual filtering to ensure relevance.
It excludes consultant positions and highlights meaningful employers.
"""

import requests
import json
import os
import time
import re
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("job_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IT_JOBS_OUTPUT = os.path.join(BASE_DIR, "it_jobs.json")
AI_JOBS_OUTPUT = os.path.join(BASE_DIR, "ai_jobs.json")
RPA_JOBS_OUTPUT = os.path.join(BASE_DIR, "rpa_jobs.json")
ALL_JOBS_OUTPUT = os.path.join(BASE_DIR, "all_jobs.json")
LAST_UPDATED_FILE = os.path.join(BASE_DIR, "last_updated.txt")
LAST_RAPIDAPI_FILE = os.path.join(BASE_DIR, "last_rapidapi.txt")

# JobTech API configuration
JOBTECH_API_URL = "https://jobsearch.api.jobtechdev.se/search"

# RapidAPI configuration for Indeed Jobs API Sweden
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"  # Replace with actual key if available
RAPIDAPI_HOST = "indeed-jobs-api-sweden.p.rapidapi.com"
RAPIDAPI_URL = "https://indeed-jobs-api-sweden.p.rapidapi.com/indeed-se"

# Search parameters
LOCATIONS = ["Göteborg", "Kungsbacka"]

# Job categories with primary and secondary keywords for contextual matching
JOB_CATEGORIES = {
    "IT": {
        "primary_keywords": [
            "systemutvecklare", "programmerare", "mjukvaruutvecklare", "software developer",
            "backend developer", "frontend developer", "fullstack developer", "devops engineer",
            "system architect", "IT-arkitekt", "IT-tekniker", "system administrator",
            "nätverkstekniker", "network engineer", "database administrator", "databasutvecklare"
        ],
        "secondary_keywords": [
            "java", "python", "c#", ".net", "javascript", "typescript", "react", "angular",
            "vue", "node.js", "php", "ruby", "go", "rust", "kotlin", "swift", "sql", "nosql",
            "mongodb", "postgresql", "mysql", "oracle", "aws", "azure", "gcp", "docker",
            "kubernetes", "linux", "windows server", "cisco", "juniper", "api", "rest",
            "microservices", "agile", "scrum", "kanban", "git", "ci/cd", "jenkins", "gitlab"
        ],
        "exclusion_keywords": [
            "konsult", "consultant", "bemanning", "rekrytering", "inhyrd", "postdoc",
            "doktorand", "phd student", "forskare", "professor", "lektor"
        ],
        "title_patterns": [
            r"utvecklare", r"developer", r"programmer", r"engineer", r"arkitekt", r"architect",
            r"tekniker", r"specialist", r"expert", r"lead", r"chef", r"manager", r"admin",
            r"administrator", r"devops", r"frontend", r"backend", r"fullstack", r"system",
            r"network", r"database", r"data", r"security", r"säkerhet", r"support"
        ]
    },
    "AI": {
        "primary_keywords": [
            "AI", "artificial intelligence", "artificiell intelligens", "machine learning",
            "maskininlärning", "deep learning", "djupinlärning", "neural networks",
            "neurala nätverk", "data scientist", "data science", "datavetenskap",
            "NLP", "natural language processing", "computer vision", "datorseende",
            "predictive analytics", "prediktiv analys", "big data", "stordata",
            "data mining", "datautvinning", "AI engineer", "ML engineer"
        ],
        "secondary_keywords": [
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
            "jupyter", "python", "r", "hadoop", "spark", "databricks", "kubeflow",
            "mlops", "reinforcement learning", "förstärkningsinlärning", "supervised learning",
            "unsupervised learning", "clustering", "classification", "regression",
            "recommendation systems", "rekommendationssystem", "anomaly detection",
            "anomalidetektering", "feature engineering", "model training", "model deployment",
            "model monitoring", "data preprocessing", "data visualization", "datavisualisering"
        ],
        "exclusion_keywords": [
            "konsult", "consultant", "bemanning", "rekrytering", "inhyrd", "postdoc",
            "doktorand", "phd student", "forskare", "professor", "lektor", "assistant professor"
        ],
        "title_patterns": [
            r"AI", r"ML", r"machine learning", r"deep learning", r"data scientist",
            r"data science", r"analytics", r"analys", r"data engineer", r"NLP",
            r"computer vision", r"neural", r"intelligence", r"intelligens"
        ]
    },
    "RPA": {
        "primary_keywords": [
            "RPA", "robotic process automation", "robotiserad processautomation",
            "process automation", "processautomation", "automation developer",
            "automationsutvecklare", "UiPath", "Blue Prism", "Automation Anywhere",
            "Microsoft Power Automate", "business process automation", "affärsprocessautomation"
        ],
        "secondary_keywords": [
            "workflow automation", "arbetsflödesautomation", "process mining", "processmining",
            "business process management", "affärsprocesshantering", "digital workforce",
            "digital arbetskraft", "intelligent automation", "intelligent automatisering",
            "hyperautomation", "hyperautomatisering", "task automation", "uppgiftsautomatisering",
            "process optimization", "processoptimering", "bot", "robot", "attended automation",
            "unattended automation", "cognitive automation", "kognitiv automatisering"
        ],
        "exclusion_keywords": [
            "konsult", "consultant", "bemanning", "rekrytering", "inhyrd", "postdoc",
            "doktorand", "phd student", "forskare", "professor", "lektor", "styr och regler",
            "reglertekniker", "DevSecOps", "DevOps", "fullstack", "frontend", "backend"
        ],
        "title_patterns": [
            r"RPA", r"automation", r"automatisering", r"robot", r"process", r"UiPath",
            r"Blue Prism", r"Automation Anywhere", r"Power Automate"
        ]
    }
}

# Meaningful employers keywords
MEANINGFUL_ORGS = [
    # Public sector
    "försvarsmakten", "polisen", "polismyndigheten", "myndighet", "kommun", 
    "region", "länsstyrelsen", "statlig", "staten", "government", "offentlig",
    "förvaltning", "departement", "riksdag", "domstol", "skatteverket",
    "arbetsförmedlingen", "försäkringskassan", "kriminalvården", "göteborgs stad",
    "västra götalandsregionen", "trafikverket", "tullverket", "migrationsverket",
    
    # Healthcare
    "sahlgrenska", "sjukhus", "vårdcentral", "folktandvården", "capio", "närhälsan",
    
    # Education
    "göteborgs universitet", "chalmers", "högskola", "gymnasium", "grundskola", "förskola",
    
    # Non-profit/NGO
    "röda korset", "rädda barnen", "stadsmissionen", "bris", "amnesty", "naturskyddsföreningen",
    
    # Research
    "forskningsinstitut", "science park", "innovatum", "rise", "ivl", "fraunhofer"
]

# Consultant keywords to exclude
CONSULTANT_KEYWORDS = [
    "konsult", "consultant", "bemanning", "rekrytering", "inhyrd", 
    "staffing", "recruitment", "consulting"
]

def search_jobtech_jobs(query, location, limit=100):
    """
    Search for jobs using the JobTech API
    
    Args:
        query (str): Search term
        location (str): Location to search in
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of job listings
    """
    logger.info(f"Searching JobTech API for '{query}' in {location}")
    
    params = {
        "q": f"{query} {location}",
        "limit": limit
    }
    
    try:
        response = requests.get(JOBTECH_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        total_hits = data.get("total", {}).get("value", 0)
        hits = data.get("hits", [])
        
        logger.info(f"Found {total_hits} total hits, retrieved {len(hits)} jobs")
        
        # Process and standardize job data
        processed_jobs = []
        for job in hits:
            processed_job = {
                "id": job.get("id"),
                "title": job.get("headline"),
                "employer": job.get("employer", {}).get("name") if job.get("employer") else "Unknown",
                "location": job.get("workplace_address", {}).get("municipality") if job.get("workplace_address") else location,
                "description": job.get("description", {}).get("text") if job.get("description") else "",
                "url": job.get("application_details", {}).get("url") if job.get("application_details") else "",
                "published": job.get("publication_date"),
                "deadline": job.get("application_deadline"),
                "is_consultant": is_consultant_job(job),
                "is_meaningful": is_meaningful_job(job),
                "source": "JobTech"
            }
            processed_jobs.append(processed_job)
        
        return processed_jobs
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching JobTech API: {e}")
        return []

def search_indeed_jobs(query, location):
    """
    Search for jobs using the Indeed API via RapidAPI
    Only used as fallback when JobTech API fails
    
    Args:
        query (str): Search term
        location (str): Location to search in
        
    Returns:
        list: List of job listings
    """
    # Check if we should use RapidAPI (only once per week)
    if not should_use_rapidapi():
        logger.info("Skipping RapidAPI call (used within the last week)")
        return []
    
    logger.info(f"Searching Indeed API for '{query}' in {location}")
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    params = {
        "search": query,
        "location": location
    }
    
    try:
        # Skip if no API key is provided
        if RAPIDAPI_KEY == "YOUR_RAPIDAPI_KEY":
            logger.warning("No RapidAPI key provided, skipping Indeed API call")
            return []
        
        response = requests.get(RAPIDAPI_URL, headers=headers, params=params)
        response.raise_for_status()
        jobs = response.json()
        
        # Update last RapidAPI usage timestamp
        update_last_rapidapi_usage()
        
        logger.info(f"Found {len(jobs)} jobs from Indeed API")
        
        # Process and standardize job data
        processed_jobs = []
        for job in jobs:
            processed_job = {
                "id": job.get("id", ""),
                "title": job.get("title", ""),
                "employer": job.get("employer", "Unknown"),
                "location": job.get("location", location),
                "description": job.get("description", ""),
                "url": job.get("url", ""),
                "published": job.get("published", datetime.now().strftime("%Y-%m-%d")),
                "deadline": job.get("deadline", ""),
                "is_consultant": is_consultant_job(job),
                "is_meaningful": is_meaningful_job(job),
                "source": "Indeed"
            }
            processed_jobs.append(processed_job)
        
        return processed_jobs
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching Indeed API: {e}")
        return []

def should_use_rapidapi():
    """
    Check if we should use RapidAPI based on last usage
    Limit to once per week to conserve API quota
    
    Returns:
        bool: True if RapidAPI should be used, False otherwise
    """
    try:
        if not os.path.exists(LAST_RAPIDAPI_FILE):
            return True
        
        with open(LAST_RAPIDAPI_FILE, "r") as f:
            last_usage = datetime.strptime(f.read().strip(), "%Y-%m-%d %H:%M:%S")
        
        # Check if it's been at least 7 days since last usage
        return datetime.now() - last_usage >= timedelta(days=7)
    
    except Exception as e:
        logger.error(f"Error checking RapidAPI usage: {e}")
        return True

def update_last_rapidapi_usage():
    """Update the last RapidAPI usage timestamp"""
    try:
        os.makedirs(os.path.dirname(LAST_RAPIDAPI_FILE), exist_ok=True)
        with open(LAST_RAPIDAPI_FILE, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("Updated last RapidAPI usage timestamp")
    except Exception as e:
        logger.error(f"Error updating RapidAPI usage timestamp: {e}")

def is_consultant_job(job):
    """Check if a job is likely a consultant position"""
    consultant_keywords = CONSULTANT_KEYWORDS
    
    # Handle different job formats (JobTech vs Indeed)
    if isinstance(job, dict):
        if "employer" in job and isinstance(job["employer"], dict):
            # JobTech format
            employer = job.get("employer", {}).get("name", "").lower()
            description = job.get("description", {}).get("text", "").lower() if isinstance(job.get("description"), dict) else ""
            title = job.get("headline", "").lower()
        else:
            # Indeed or processed format
            employer = str(job.get("employer", "")).lower()
            description = str(job.get("description", "")).lower()
            title = str(job.get("title", "")).lower()
    else:
        return False
    
    for keyword in consultant_keywords:
        if keyword in employer or keyword in description or keyword in title:
            return True
    return False

def is_meaningful_job(job):
    """Check if a job is from a meaningful organization"""
    meaningful_keywords = MEANINGFUL_ORGS
    
    # Handle different job formats (JobTech vs Indeed)
    if isinstance(job, dict):
        if "employer" in job and isinstance(job["employer"], dict):
            # JobTech format
            employer = job.get("employer", {}).get("name", "").lower()
            description = job.get("description", {}).get("text", "").lower() if isinstance(job.get("description"), dict) else ""
            title = job.get("headline", "").lower()
        else:
            # Indeed or processed format
            employer = str(job.get("employer", "")).lower()
            description = str(job.get("description", "")).lower()
            title = str(job.get("title", "")).lower()
    else:
        return False
    
    for keyword in meaningful_keywords:
        if keyword in employer or keyword in description or keyword in title:
            return True
    return False

def calculate_relevance_score(job, category):
    """
    Calculate a relevance score for a job based on how well it matches a category
    
    Args:
        job (dict): Job data
        category (str): Category to match against (IT, AI, or RPA)
        
    Returns:
        float: Relevance score between 0 and 1
    """
    if category not in JOB_CATEGORIES:
        return 0.0
    
    # Get job text fields
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    employer = job.get("employer", "").lower()
    
    # Get category keywords
    primary_keywords = JOB_CATEGORIES[category]["primary_keywords"]
    secondary_keywords = JOB_CATEGORIES[category]["secondary_keywords"]
    exclusion_keywords = JOB_CATEGORIES[category]["exclusion_keywords"]
    title_patterns = JOB_CATEGORIES[category]["title_patterns"]
    
    # Check for exclusion keywords
    for keyword in exclusion_keywords:
        if keyword in title:
            return 0.0
    
    # Initialize score components
    title_score = 0.0
    primary_score = 0.0
    secondary_score = 0.0
    
    # Check title patterns (highest weight)
    for pattern in title_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            title_score = 1.0
            break
    
    # Check primary keywords
    primary_matches = 0
    for keyword in primary_keywords:
        if keyword in title:
            primary_matches += 3  # Higher weight for title matches
        elif keyword in description:
            primary_matches += 1
    primary_score = min(1.0, primary_matches / (len(primary_keywords) * 0.5))
    
    # Check secondary keywords
    secondary_matches = 0
    for keyword in secondary_keywords:
        if keyword in title:
            secondary_matches += 2  # Higher weight for title matches
        elif keyword in description:
            secondary_matches += 0.5
    secondary_score = min(1.0, secondary_matches / (len(secondary_keywords) * 0.5))
    
    # Calculate final score with weights
    final_score = (title_score * 0.5) + (primary_score * 0.35) + (secondary_score * 0.15)
    
    return final_score

def is_job_relevant_for_category(job, category, min_score=0.3):
    """
    Determine if a job is relevant for a specific category
    
    Args:
        job (dict): Job data
        category (str): Category to check relevance for
        min_score (float): Minimum relevance score threshold
        
    Returns:
        bool: True if job is relevant for category, False otherwise
    """
    score = calculate_relevance_score(job, category)
    return score >= min_score

def scrape_jobs(category, search_terms, locations):
    """
    Scrape jobs for a specific category and search terms
    
    Args:
        category (str): Job category (IT, AI, or RPA)
        search_terms (list): List of search terms
        locations (list): List of locations to search in
        
    Returns:
        list: List of jobs matching the criteria
    """
    all_jobs = []
    unique_job_ids = set()
    
    for location in locations:
        logger.info(f"\nSearching for {category} jobs in {location}...")
        
        for term in search_terms:
            logger.info(f"  Searching for term: {term}")
            
            # First try JobTech API
            jobs = search_jobtech_jobs(term, location)
            
            # If JobTech fails, try Indeed API as fallback
            if not jobs:
                logger.warning(f"JobTech API returned no results for '{term}' in {location}, trying Indeed API")
                jobs = search_indeed_jobs(term, location)
            
            if not jobs:
                logger.warning(f"No jobs found for term: {term}")
                continue
            
            logger.info(f"  Found {len(jobs)} jobs for term: {term}")
            
            # Process jobs with advanced filtering
            for job in jobs:
                # Skip if already processed
                if job["id"] in unique_job_ids:
                    continue
                
                # Skip consultant jobs
                if job["is_consultant"]:
                    continue
                
                # Apply advanced relevance filtering
                if is_job_relevant_for_category(job, category):
                    # Add relevance score and category
                    job["relevance_score"] = calculate_relevance_score(job, category)
                    job["category"] = category
                    all_jobs.append(job)
                    unique_job_ids.add(job["id"])
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
    
    # Sort by relevance score (highest first)
    all_jobs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return all_jobs

def save_jobs(jobs, output_file):
    """Save jobs to a JSON file"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {len(jobs)} jobs to {output_file}")

def update_last_updated():
    """Update the last_updated.txt file with current timestamp"""
    with open(LAST_UPDATED_FILE, "w", encoding="utf-8") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info(f"Updated last_updated.txt with current timestamp")

def main():
    logger.info(f"Starting job scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Scrape IT jobs
    it_jobs = scrape_jobs("IT", JOB_CATEGORIES["IT"]["primary_keywords"], LOCATIONS)
    logger.info(f"\nFound {len(it_jobs)} relevant IT jobs in Gothenburg and Kungsbacka")
    save_jobs(it_jobs, IT_JOBS_OUTPUT)
    
    # Scrape AI jobs
    ai_jobs = scrape_jobs("AI", JOB_CATEGORIES["AI"]["primary_keywords"], LOCATIONS)
    logger.info(f"\nFound {len(ai_jobs)} relevant AI jobs in Gothenburg and Kungsbacka")
    save_jobs(ai_jobs, AI_JOBS_OUTPUT)
    
    # Scrape RPA jobs
    rpa_jobs = scrape_jobs("RPA", JOB_CATEGORIES["RPA"]["primary_keywords"], LOCATIONS)
    logger.info(f"\nFound {len(rpa_jobs)} relevant RPA jobs in Gothenburg and Kungsbacka")
    save_jobs(rpa_jobs, RPA_JOBS_OUTPUT)
    
    # Combine all jobs
    all_jobs = it_jobs + ai_jobs + rpa_jobs
    logger.info(f"\nFound {len(all_jobs)} total relevant jobs in Gothenburg and Kungsbacka")
    save_jobs(all_jobs, ALL_JOBS_OUTPUT)
    
    # Update last updated timestamp
    update_last_updated()
    
    logger.info(f"\nJob scraping completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
