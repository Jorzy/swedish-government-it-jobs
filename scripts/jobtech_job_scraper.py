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
            "doktorand", "phd student", "forskare", "professor", "lektor",
            "DevSecOps", "DevOps", "fullstack", "frontend", "backend"
        ],
        "title_patterns": [
            r"utvecklare", r"developer", r"programmer", r"engineer", r"arkitekt", r"architect",
            r"tekniker", r"specialist", r"expert", r"lead", r"chef", r"manager", r"admin",
            r"administrator", r"system",
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
    "konsult", "consultant", "consulting", "konsultbolag", "konsultföretag",
    "konsultuppdrag", "konsultation", "bemanning", "rekrytering",
    "interim", "inhyrd", "resurskonsult", "underkonsult", "staffing",
    "konsulttjänst", "konsultchef", "konsultledare",
    "till vår kund", "hos kund", "till våra kunder", 
    "consultant role", "konsultroll", "konsultuppdrag",
    "för kunds räkning", "placerad hos", "placering hos"
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
    logger.info(f"Searching JobTech API for \'{query}\' in {location}")
    
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
    
    logger.info(f"Searching Indeed API for \'{query}\' in {location}")
    
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
        
        # Check if it\'s been at least 7 days since last usage
        return datetime.now() - last_usage >= timedelta(days=7)
    
    except Exception as e:
        logger.error(f"Error checking RapidAPI usage: {e}")
        return True

def update_last_rapidapi_usage():
    """
    Update the last RapidAPI usage timestamp
    """
    try:
        os.makedirs(os.path.dirname(LAST_RAPIDAPI_FILE), exist_ok=True)
        with open(LAST_RAPIDAPI_FILE, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("Updated last RapidAPI usage timestamp")
    except Exception as e:
        logger.error(f"Error updating RapidAPI usage timestamp: {e}")

def is_consultant_job(job):
    """
    Check if a job is likely a consultant position with improved detection
    """
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
    
    text_to_check = (title + " " + description + " " + employer).lower()
    
    # Direct consultant indicators
    for pattern in CONSULTANT_KEYWORDS:
        if pattern in text_to_check:
            return True
            
    return False

def is_meaningful_job(job):
    """
    Check if a job is from a meaningful organization
    """
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
        if keyword in title or keyword in description:
            return 0.0
    
    # Initialize score components
    title_score = 0.0
    primary_score = 0.0
    secondary_score = 0.0
    
    # Title pattern matching (strongest indicator)
    for pattern in title_patterns:
        if re.search(pattern, title):
            title_score = 0.8 # High score for title match
            break
            
    # Primary keyword matching
    for keyword in primary_keywords:
        if keyword in title:
            primary_score += 0.4
        elif keyword in description:
            primary_score += 0.2
            
    # Secondary keyword matching
    for keyword in secondary_keywords:
        if keyword in title:
            secondary_score += 0.2
        elif keyword in description:
            secondary_score += 0.1
            
    # Combine scores, cap at 1.0
    relevance = min(1.0, title_score + primary_score + secondary_score)
    
    return relevance

def filter_and_categorize_jobs(all_jobs):
    """
    Filter and categorize jobs into IT, AI, and RPA
    
    Args:
        all_jobs (list): List of all job listings
        
    Returns:
        tuple: (it_jobs, ai_jobs, rpa_jobs, all_filtered_jobs)
    """
    it_jobs = []
    ai_jobs = []
    rpa_jobs = []
    all_filtered_jobs = []
    
    for job in all_jobs:
        # Exclude consultant positions first
        if is_consultant_job(job):
            continue
            
        # Calculate relevance for each category
        it_relevance = calculate_relevance_score(job, "IT")
        ai_relevance = calculate_relevance_score(job, "AI")
        rpa_relevance = calculate_relevance_score(job, "RPA")
        
        # Determine the best category and assign score
        best_category = None
        max_relevance = 0.0
        
        if it_relevance >= 0.6 and it_relevance > max_relevance:
            best_category = "IT"
            max_relevance = it_relevance
        if ai_relevance >= 0.6 and ai_relevance > max_relevance:
            best_category = "AI"
            max_relevance = ai_relevance
        if rpa_relevance >= 0.6 and rpa_relevance > max_relevance:
            best_category = "RPA"
            max_relevance = rpa_relevance
            
        if best_category:
            job["category"] = best_category
            job["relevance_score"] = int(max_relevance * 100) # Convert to percentage
            all_filtered_jobs.append(job)
            
            if best_category == "IT":
                it_jobs.append(job)
            elif best_category == "AI":
                ai_jobs.append(job)
            elif best_category == "RPA":
                rpa_jobs.append(job)
                
    return it_jobs, ai_jobs, rpa_jobs, all_filtered_jobs

def save_jobs_to_json(jobs, filename):
    """
    Save job listings to a JSON file
    
    Args:
        jobs (list): List of job listings
        filename (str): Name of the JSON file
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved {len(jobs)} jobs to {filename}")
    except Exception as e:
        logger.error(f"Error saving jobs to {filename}: {e}")

def main():
    logger.info("Starting job scraping process...")
    
    all_fetched_jobs = []
    
    # Search for IT jobs
    for location in LOCATIONS:
        all_fetched_jobs.extend(search_jobtech_jobs("IT-utvecklare", location))
        all_fetched_jobs.extend(search_jobtech_jobs("programmerare", location))
        all_fetched_jobs.extend(search_jobtech_jobs("systemutvecklare", location))
        all_fetched_jobs.extend(search_jobtech_jobs("mjukvaruutvecklare", location))
        
    # Search for AI jobs
    for location in LOCATIONS:
        all_fetched_jobs.extend(search_jobtech_jobs("AI", location))
        all_fetched_jobs.extend(search_jobtech_jobs("maskininlärning", location))
        all_fetched_jobs.extend(search_jobtech_jobs("data scientist", location))
        
    # Search for RPA jobs (with UiPath focus)
    for location in LOCATIONS:
        all_fetched_jobs.extend(search_jobtech_jobs("RPA", location))
        all_fetched_jobs.extend(search_jobtech_jobs("UiPath", location))
        all_fetched_jobs.extend(search_jobtech_jobs("automationsutvecklare", location))
        
    # Deduplicate jobs
    unique_jobs = {job["id"]: job for job in all_fetched_jobs}.values()
    logger.info(f"Found {len(unique_jobs)} unique jobs before filtering")
    
    # Filter and categorize jobs
    it_jobs, ai_jobs, rpa_jobs, all_filtered_jobs = filter_and_categorize_jobs(list(unique_jobs))
    
    # Save categorized jobs
    save_jobs_to_json(it_jobs, IT_JOBS_OUTPUT)
    save_jobs_to_json(ai_jobs, AI_JOBS_OUTPUT)
    save_jobs_to_json(rpa_jobs, RPA_JOBS_OUTPUT)
    save_jobs_to_json(all_filtered_jobs, ALL_JOBS_OUTPUT)
    
    # Update last updated timestamp
    try:
        with open(LAST_UPDATED_FILE, "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))
        logger.info("Updated last updated timestamp")
    except Exception as e:
        logger.error(f"Error updating last updated timestamp: {e}")
        
    logger.info("Job scraping process completed.")

if __name__ == "__main__":
    main()


