#!/usr/bin/env python3
"""
Enhanced Job Scraper with Advanced Filtering for IT, AI, and RPA Jobs
Focuses on Gothenburg and Kungsbacka with strict relevance criteria
Includes special handling for UiPath-related positions
Excludes DevOps-related positions
"""

import requests
import json
import logging
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("job_scraper.log"),
        logging.StreamHandler()
    ]
)

# Constants
JOBTECH_API_URL = "https://jobsearch.api.jobtechdev.se/search"
INDEED_API_URL = "https://indeed-jobs-api.p.rapidapi.com/indeed-se/"
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"  # Replace with your actual RapidAPI key if using Indeed API
RAPIDAPI_HOST = "indeed-jobs-api.p.rapidapi.com"

# Location codes
GOTHENBURG_CODE = "1480"  # Göteborg kommun code
KUNGSBACKA_CODE = "1384"  # Kungsbacka kommun code

# Search terms for different job categories
IT_SEARCH_TERMS = [
    "systemutvecklare", "programmerare", "mjukvaruutvecklare", 
    "software developer", "backend developer", "frontend developer", 
    "fullstack developer", "system architect", "IT-arkitekt", 
    "IT-tekniker", "system administrator", "nätverkstekniker", 
    "network engineer", "database administrator", "databasutvecklare"
]

AI_SEARCH_TERMS = [
    "AI", "artificial intelligence", "machine learning", "deep learning", 
    "data scientist", "data science", "ML engineer", "AI engineer", 
    "NLP", "natural language processing", "computer vision", 
    "neural networks", "maskininlärning", "artificiell intelligens"
]

RPA_SEARCH_TERMS = [
    "RPA", "robotic process automation", "automation developer", 
    "automationsutvecklare", "UiPath", "Blue Prism", "Automation Anywhere", 
    "Microsoft Power Automate", "business process automation", 
    "affärsprocessautomation"
]

# Exclusion patterns (jobs containing these in title or description will be filtered out)
EXCLUSION_PATTERNS = [
    r'\bconsult(ant)?\b', r'\bkonsult\b', r'\bpostdoc\b', r'\bpost-doc\b', 
    r'\bphd\b', r'\bdoktorand\b', r'\bforskare\b', r'\bresearcher\b',
    r'\bprofessor\b', r'\blecturer\b', r'\bteaching\b', r'\bundervisning\b',
    r'\bdevops\b', r'\bdev-ops\b', r'\bdev ops\b', r'\bsite reliability\b', r'\bsre\b',
    r'\bcloud engineer\b', r'\bcloud operations\b', r'\binfrastructure engineer\b'
]

# Required title patterns for each category (jobs must match at least one pattern to be included)
IT_TITLE_PATTERNS = [
    r'\bdeveloper\b', r'\butvecklare\b', r'\bprogramm(er|erare)\b', 
    r'\bsoftware\b', r'\bmjukvaru\b', r'\bsystem\b', r'\barkitekt\b', 
    r'\bIT\b', r'\btekniker\b', r'\badministrator\b', r'\bengine(er|ör)\b',
    r'\bfullstack\b', r'\bfrontend\b', r'\bbackend\b', r'\bdatabas\b'
]

AI_TITLE_PATTERNS = [
    r'\bAI\b', r'\bartificial intelligence\b', r'\bmachine learning\b', 
    r'\bdeep learning\b', r'\bdata scien(ce|tist)\b', r'\bML\b', 
    r'\bNLP\b', r'\bnatural language\b', r'\bcomputer vision\b', 
    r'\bneural network\b', r'\bmaskininlärning\b', r'\bartificiell intelligens\b'
]

RPA_TITLE_PATTERNS = [
    r'\bRPA\b', r'\brobotic process\b', r'\bautomation\b', 
    r'\bautomations\b', r'\bUiPath\b', r'\bBlue Prism\b', 
    r'\bAutomation Anywhere\b', r'\bPower Automate\b', 
    r'\bprocess automation\b', r'\bprocessautomation\b'
]

# Secondary patterns (boost relevance score if these are found in description)
IT_SECONDARY_PATTERNS = [
    r'\bJava\b', r'\bPython\b', r'\bC#\b', r'\bJavaScript\b', r'\bTypeScript\b',
    r'\bReact\b', r'\bAngular\b', r'\bVue\b', r'\bNode\.js\b', r'\bASP\.NET\b',
    r'\bSQL\b', r'\bNoSQL\b', r'\bMongoDB\b', r'\bPostgreSQL\b', r'\bMySQL\b',
    r'\bAPI\b', r'\bREST\b', r'\bGit\b', r'\bCI/CD\b', r'\bAgile\b', r'\bScrum\b',
    r'\bkodning\b', r'\bprogrammering\b', r'\butveckling\b', r'\bsystemutveckling\b'
]

AI_SECONDARY_PATTERNS = [
    r'\bTensorFlow\b', r'\bPyTorch\b', r'\bKeras\b', r'\bscikit-learn\b',
    r'\bdata mining\b', r'\bpredictive model\b', r'\bprediktiv\b', r'\balgoritm\b',
    r'\bstatistical analysis\b', r'\bstatistisk analys\b', r'\bdata processing\b',
    r'\bfeature engineering\b', r'\bneural network\b', r'\bneurala nätverk\b',
    r'\bGPT\b', r'\bLLM\b', r'\blarge language model\b', r'\btransformer\b',
    r'\bcomputer vision\b', r'\bimage recognition\b', r'\bbildigenkänning\b'
]

RPA_SECONDARY_PATTERNS = [
    r'\bUiPath\b', r'\bUiPath Studio\b', r'\bUiPath Orchestrator\b',
    r'\bBlue Prism\b', r'\bAutomation Anywhere\b', r'\bPower Automate\b',
    r'\bworkflow automation\b', r'\bprocess mining\b', r'\bautomatisering\b',
    r'\bbusiness process\b', r'\baffärsprocess\b', r'\bbot\b', r'\brobot\b',
    r'\bautomated task\b', r'\bautomatiserade uppgifter\b', r'\bscripting\b',
    r'\bmacro\b', r'\bmakro\b', r'\bprocess efficiency\b', r'\beffektivisering\b'
]

# Meaningful employer keywords
MEANINGFUL_EMPLOYER_PATTERNS = [
    r'\bkommun\b', r'\bregion\b', r'\blandsting\b', r'\bstat\b', r'\bmyndighet\b',
    r'\bförsvarsmakten\b', r'\bpolisen\b', r'\bsjukhus\b', r'\bvård\b', r'\bskola\b',
    r'\butbildning\b', r'\bforskningsinstitut\b', r'\buniversitet\b', r'\bhögskola\b',
    r'\bsamhäll\b', r'\bpublic service\b', r'\bstatlig\b', r'\boffentlig\b',
    r'\bsamhällsnytta\b', r'\bhållbar\b', r'\bsustainable\b', r'\bmiljö\b',
    r'\benvironment\b', r'\bsocial\b', r'\bwelfare\b', r'\bvälfärd\b'
]

# List of meaningful employers (exact matches)
MEANINGFUL_EMPLOYERS = [
    "Försvarsmakten", "Polisen", "Göteborgs Stad", "Västra Götalandsregionen",
    "Kungsbacka kommun", "Trafikverket", "Skatteverket", "Migrationsverket",
    "Arbetsförmedlingen", "Försäkringskassan", "Sahlgrenska", "Chalmers",
    "Göteborgs universitet", "Länsstyrelsen", "SVT", "SR", "Naturvårdsverket",
    "Energimyndigheten", "SMHI", "Havs- och vattenmyndigheten", "MSB",
    "Myndigheten för digital förvaltning", "Pensionsmyndigheten", "CSN",
    "Kronofogden", "Tullverket", "Kriminalvården", "Domstolsverket",
    "Folkhälsomyndigheten", "Socialstyrelsen", "Skolverket", "Lantmäteriet"
]

def search_jobtech_api(search_term: str, location: str) -> List[Dict[str, Any]]:
    """
    Search the JobTech API for jobs matching the given search term and location.
    
    Args:
        search_term: The search term to look for
        location: The location to search in (kommun code)
        
    Returns:
        A list of job dictionaries
    """
    logging.info(f"Searching JobTech API for '{search_term}' in {location}")
    
    params = {
        "q": search_term,
        "municipality": location,
        "limit": 100,
        "sort": "relevance"
    }
    
    try:
        response = requests.get(JOBTECH_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        total_hits = data.get("total", {}).get("value", 0)
        jobs = data.get("hits", [])
        
        logging.info(f"Found {total_hits} total hits, retrieved {len(jobs)} jobs")
        return jobs
    except Exception as e:
        logging.error(f"Error searching JobTech API: {e}")
        return []

def search_indeed_api(search_term: str, location: str) -> List[Dict[str, Any]]:
    """
    Search the Indeed API for jobs matching the given search term and location.
    Only used as a fallback when JobTech API fails.
    
    Args:
        search_term: The search term to look for
        location: The location to search in (city name)
        
    Returns:
        A list of job dictionaries
    """
    logging.info(f"Searching Indeed API for '{search_term}' in {location}")
    
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "YOUR_RAPIDAPI_KEY":
        logging.warning("No RapidAPI key provided, skipping Indeed API call")
        return []
    
    # Convert kommun code to city name
    city = "Göteborg" if location == GOTHENBURG_CODE else "Kungsbacka"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    params = {
        "search_term": search_term,
        "location": city,
        "page": "1",
        "filter_job_type": "fulltime"
    }
    
    try:
        response = requests.get(INDEED_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        jobs = data.get("jobs", [])
        logging.info(f"Found {len(jobs)} jobs from Indeed API")
        return jobs
    except Exception as e:
        logging.error(f"Error searching Indeed API: {e}")
        return []

def is_consultant_position(job: Dict[str, Any]) -> bool:
    """
    Check if a job is a consultant position.
    
    Args:
        job: The job dictionary
        
    Returns:
        True if the job is a consultant position, False otherwise
    """
    title = job.get("headline", job.get("title", "")).lower()
    
    # Handle description which might be a dict or string
    description_raw = job.get("description", "")
    if isinstance(description_raw, dict):
        description = description_raw.get("text", "").lower()
    elif isinstance(description_raw, str):
        description = description_raw.lower()
    else:
        description = ""
    
    # Handle employer which might be a dict or string
    employer_raw = job.get("employer", "")
    if isinstance(employer_raw, dict):
        employer = employer_raw.get("name", "").lower()
    elif isinstance(employer_raw, str):
        employer = employer_raw.lower()
    else:
        employer = ""
    
    consultant_keywords = ["konsult", "consultant", "consulting"]
    
    # Check title
    if any(keyword in title for keyword in consultant_keywords):
        return True
    
    # Check employer name
    if any(keyword in employer for keyword in consultant_keywords):
        return True
    
    # Check for common consulting firms
    consulting_firms = [
        "accenture", "capgemini", "cognizant", "deloitte", "ey", "kpmg", "pwc",
        "mckinsey", "bcg", "bain", "tcs", "infosys", "wipro", "hcl", "ibm",
        "tieto", "evry", "sopra steria", "cgi", "sigma", "knowit", "hiq",
        "cybercom", "b3", "consid", "softronic", "netlight", "tretton37"
    ]
    
    if any(firm in employer for firm in consulting_firms):
        return True
    
    # Check description for consultant indicators
    consultant_phrases = [
        "konsultuppdrag", "consultant assignment", "consulting assignment",
        "konsultroll", "consultant role", "consulting role",
        "konsulttjänst", "consultant service", "consulting service"
    ]
    
    if any(phrase in description for phrase in consultant_phrases):
        return True
    
    return False

def is_meaningful_employer(employer_name: str, description: str) -> bool:
    """
    Check if an employer is considered meaningful (government, public service, etc.)
    
    Args:
        employer_name: The name of the employer
        description: The job description
        
    Returns:
        True if the employer is meaningful, False otherwise
    """
    # Check if employer is in the list of meaningful employers
    if any(employer.lower() in employer_name.lower() for employer in MEANINGFUL_EMPLOYERS):
        return True
    
    # Check for meaningful employer patterns in the name
    if any(re.search(pattern, employer_name.lower()) for pattern in MEANINGFUL_EMPLOYER_PATTERNS):
        return True
    
    # Check for meaningful employer patterns in the description
    if any(re.search(pattern, description.lower()) for pattern in MEANINGFUL_EMPLOYER_PATTERNS):
        return True
    
    return False

def calculate_relevance_score(job: Dict[str, Any], category: str) -> float:
    """
    Calculate a relevance score for a job based on how well it matches the category.
    
    Args:
        job: The job dictionary
        category: The job category (IT, AI, or RPA)
        
    Returns:
        A relevance score between 0 and 1
    """
    title = job.get("headline", job.get("title", ""))
    
    # Handle description which might be a dict or string
    description_raw = job.get("description", "")
    if isinstance(description_raw, dict):
        description = description_raw.get("text", "")
    elif isinstance(description_raw, str):
        description = description_raw
    else:
        description = ""
    
    # Combine title and description for pattern matching
    text = f"{title} {description}"
    
    # Select the appropriate patterns based on category
    if category == "IT":
        title_patterns = IT_TITLE_PATTERNS
        secondary_patterns = IT_SECONDARY_PATTERNS
    elif category == "AI":
        title_patterns = AI_TITLE_PATTERNS
        secondary_patterns = AI_SECONDARY_PATTERNS
    elif category == "RPA":
        title_patterns = RPA_TITLE_PATTERNS
        secondary_patterns = RPA_SECONDARY_PATTERNS
    else:
        return 0.0
    
    # Check for exclusion patterns
    for pattern in EXCLUSION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            # Special exception for UiPath in RPA category
            if category == "RPA" and "UiPath" in title:
                # Don't exclude UiPath jobs from RPA category even if they match exclusion patterns
                pass
            else:
                return 0.0
    
    # Check for required title patterns
    title_match = False
    for pattern in title_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            title_match = True
            break
    
    # Special case for UiPath in RPA category
    if category == "RPA" and "UiPath" in title:
        title_match = True
    
    # If no title match, the job is not relevant
    if not title_match:
        return 0.0
    
    # Calculate base score from title match
    score = 0.5
    
    # Add points for secondary pattern matches
    secondary_matches = 0
    for pattern in secondary_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            secondary_matches += 1
    
    # Add up to 0.4 points based on secondary matches
    score += min(secondary_matches / 10, 0.4)
    
    # Add 0.1 points if the job is from a meaningful employer
    # Handle employer which might be a dict or string
    employer_raw = job.get("employer", "")
    if isinstance(employer_raw, dict):
        employer_name = employer_raw.get("name", "")
    elif isinstance(employer_raw, str):
        employer_name = employer_raw
    else:
        employer_name = ""
        
    if is_meaningful_employer(employer_name, description):
        score += 0.1
    
    # Special boost for UiPath in RPA category
    if category == "RPA" and "UiPath" in text:
        score += 0.2
    
    # Cap the score at 1.0
    return min(score, 1.0)

def normalize_job(job: Dict[str, Any], source: str, category: str) -> Dict[str, Any]:
    """
    Normalize job data from different sources into a consistent format.
    
    Args:
        job: The job dictionary
        source: The source of the job data (JobTech or Indeed)
        category: The job category (IT, AI, or RPA)
        
    Returns:
        A normalized job dictionary
    """
    if source == "JobTech":
        # Extract relevant fields from JobTech API response
        job_id = job.get("id", "")
        title = job.get("headline", "")
        
        # Handle employer which might be a dict or string
        employer_raw = job.get("employer", {})
        if isinstance(employer_raw, dict):
            employer_name = employer_raw.get("name", "")
        else:
            employer_name = str(employer_raw)
        
        # Handle location which might be nested
        workplace_address = job.get("workplace_address", {})
        if isinstance(workplace_address, dict):
            location = workplace_address.get("municipality", "")
        else:
            location = "Göteborg"  # Default to Göteborg if not specified
        
        # Handle description which might be a dict or string
        description_raw = job.get("description", {})
        if isinstance(description_raw, dict):
            description = description_raw.get("text", "")
        else:
            description = str(description_raw)
        
        # Handle application details which might be nested
        application_details = job.get("application_details", {})
        if isinstance(application_details, dict):
            url = application_details.get("url", "")
        else:
            url = ""
        
        published = job.get("publication_date", "")
        deadline = job.get("application_deadline", "")
    else:  # Indeed
        # Extract relevant fields from Indeed API response
        job_id = job.get("job_id", "")
        title = job.get("job_title", "")
        employer_name = job.get("company_name", "")
        location = job.get("location", "")
        description = job.get("description", "")
        url = job.get("job_url", "")
        published = job.get("posted_at", "")
        deadline = ""  # Indeed doesn't provide deadline
    
    # Calculate relevance score
    relevance_score = calculate_relevance_score(job, category)
    
    # Check if it's a consultant position
    is_consultant = is_consultant_position(job)
    
    # Check if it's a meaningful employer
    is_meaningful = is_meaningful_employer(employer_name, description)
    
    return {
        "id": job_id,
        "title": title,
        "employer": employer_name,
        "location": location,
        "description": description,
        "url": url,
        "published": published,
        "deadline": deadline,
        "is_consultant": is_consultant,
        "is_meaningful": is_meaningful,
        "source": source,
        "relevance_score": relevance_score,
        "category": category
    }

def search_jobs(search_terms: List[str], location: str, category: str) -> List[Dict[str, Any]]:
    """
    Search for jobs matching the given search terms and location.
    
    Args:
        search_terms: The search terms to look for
        location: The location to search in (kommun code)
        category: The job category (IT, AI, or RPA)
        
    Returns:
        A list of normalized job dictionaries
    """
    all_jobs = []
    
    for term in search_terms:
        logging.info(f"  Searching for term: {term}")
        
        # Try JobTech API first
        jobs = search_jobtech_api(term, location)
        
        # If JobTech API fails or returns no results, try Indeed API as fallback
        if not jobs:
            logging.warning(f"JobTech API returned no results for '{term}' in {location}, trying Indeed API")
            jobs = search_indeed_api(term, location)
            source = "Indeed"
        else:
            source = "JobTech"
        
        # Normalize job data
        normalized_jobs = [normalize_job(job, source, category) for job in jobs]
        
        # Filter out consultant positions
        filtered_jobs = [job for job in normalized_jobs if not job["is_consultant"]]
        
        # Add to all jobs
        all_jobs.extend(filtered_jobs)
        
        # Add a small delay to avoid rate limiting
        time.sleep(1)
    
    return all_jobs

def filter_and_deduplicate_jobs(jobs: List[Dict[str, Any]], min_relevance: float = 0.6) -> List[Dict[str, Any]]:
    """
    Filter jobs by relevance score and remove duplicates.
    
    Args:
        jobs: The list of jobs to filter
        min_relevance: The minimum relevance score to include
        
    Returns:
        A filtered and deduplicated list of jobs
    """
    # Filter by relevance score
    relevant_jobs = [job for job in jobs if job["relevance_score"] >= min_relevance]
    
    # Remove duplicates based on job ID
    seen_ids = set()
    deduplicated_jobs = []
    
    for job in relevant_jobs:
        if job["id"] not in seen_ids:
            seen_ids.add(job["id"])
            deduplicated_jobs.append(job)
    
    return deduplicated_jobs

def main():
    """Main function to scrape and filter jobs."""
    logging.info(f"\nJob scraping started at {datetime.now()}")
    
    # Search for IT jobs in Gothenburg
    logging.info("\nSearching for IT jobs in Gothenburg...")
    it_jobs_gothenburg = search_jobs(IT_SEARCH_TERMS, GOTHENBURG_CODE, "IT")
    
    # Search for IT jobs in Kungsbacka
    logging.info("\nSearching for IT jobs in Kungsbacka...")
    it_jobs_kungsbacka = search_jobs(IT_SEARCH_TERMS, KUNGSBACKA_CODE, "IT")
    
    # Search for AI jobs in Gothenburg
    logging.info("\nSearching for AI jobs in Gothenburg...")
    ai_jobs_gothenburg = search_jobs(AI_SEARCH_TERMS, GOTHENBURG_CODE, "AI")
    
    # Search for AI jobs in Kungsbacka
    logging.info("\nSearching for AI jobs in Kungsbacka...")
    ai_jobs_kungsbacka = search_jobs(AI_SEARCH_TERMS, KUNGSBACKA_CODE, "AI")
    
    # Search for RPA jobs in Gothenburg
    logging.info("\nSearching for RPA jobs in Gothenburg...")
    rpa_jobs_gothenburg = search_jobs(RPA_SEARCH_TERMS, GOTHENBURG_CODE, "RPA")
    
    # Search for RPA jobs in Kungsbacka
    logging.info("\nSearching for RPA jobs in Kungsbacka...")
    rpa_jobs_kungsbacka = search_jobs(RPA_SEARCH_TERMS, KUNGSBACKA_CODE, "RPA")
    
    # Combine all jobs
    all_it_jobs = it_jobs_gothenburg + it_jobs_kungsbacka
    all_ai_jobs = ai_jobs_gothenburg + ai_jobs_kungsbacka
    all_rpa_jobs = rpa_jobs_gothenburg + rpa_jobs_kungsbacka
    
    # Filter and deduplicate jobs
    filtered_it_jobs = filter_and_deduplicate_jobs(all_it_jobs)
    filtered_ai_jobs = filter_and_deduplicate_jobs(all_ai_jobs)
    filtered_rpa_jobs = filter_and_deduplicate_jobs(all_rpa_jobs)
    
    # Combine all filtered jobs
    all_filtered_jobs = filtered_it_jobs + filtered_ai_jobs + filtered_rpa_jobs
    
    # Save jobs to JSON files
    with open("it_jobs.json", "w", encoding="utf-8") as f:
        json.dump(filtered_it_jobs, f, ensure_ascii=False, indent=2)
    
    with open("ai_jobs.json", "w", encoding="utf-8") as f:
        json.dump(filtered_ai_jobs, f, ensure_ascii=False, indent=2)
    
    with open("rpa_jobs.json", "w", encoding="utf-8") as f:
        json.dump(filtered_rpa_jobs, f, ensure_ascii=False, indent=2)
    
    with open("all_jobs.json", "w", encoding="utf-8") as f:
        json.dump(all_filtered_jobs, f, ensure_ascii=False, indent=2)
    
    # Update last updated timestamp
    with open("last_updated.txt", "w", encoding="utf-8") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Log results
    logging.info(f"\nFound {len(filtered_it_jobs)} highly relevant IT jobs in Gothenburg and Kungsbacka")
    logging.info(f"Saved {len(filtered_it_jobs)} jobs to it_jobs.json")
    
    logging.info(f"\nFound {len(filtered_ai_jobs)} highly relevant AI jobs in Gothenburg and Kungsbacka")
    logging.info(f"Saved {len(filtered_ai_jobs)} jobs to ai_jobs.json")
    
    logging.info(f"\nFound {len(filtered_rpa_jobs)} highly relevant RPA jobs in Gothenburg and Kungsbacka")
    logging.info(f"Saved {len(filtered_rpa_jobs)} jobs to rpa_jobs.json")
    
    logging.info(f"\nFound {len(all_filtered_jobs)} total highly relevant jobs in Gothenburg and Kungsbacka")
    logging.info(f"Saved {len(all_filtered_jobs)} jobs to all_jobs.json")
    
    logging.info("Updated last_updated.txt with current timestamp")
    
    logging.info(f"\nJob scraping completed at {datetime.now()}")

if __name__ == "__main__":
    main()
