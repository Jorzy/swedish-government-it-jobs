#!/usr/bin/env python3
"""
Job Filter Module for GitHub Pages

This module provides enhanced filtering capabilities for IT/programming jobs in Gothenburg,
with specific focus on excluding consultant positions.
"""

import json
import re
from datetime import datetime
import os

class JobFilter:
    """Class to filter jobs based on various criteria"""
    
    def __init__(self):
        # Government organization keywords (expanded list)
        self.gov_keywords = [
            "försvarsmakten", "polisen", "polismyndigheten", "myndighet", "kommun", 
            "region", "länsstyrelsen", "statlig", "staten", "government", "offentlig",
            "förvaltning", "departement", "riksdag", "domstol", "skatteverket",
            "arbetsförmedlingen", "försäkringskassan", "kriminalvården", "göteborgs stad",
            "västra götalandsregionen", "trafikverket", "tullverket", "migrationsverket",
            "universitet", "högskola", "chalmers", "göteborgs universitet", "sahlgrenska",
            "räddningstjänsten", "sjukhus", "säpo", "myndigheten för", "verket för"
        ]
        
        # Consultant keywords to exclude (expanded list)
        self.consultant_keywords = [
            "konsult", "consultant", "bemanning", "rekrytering", "inhyrd", 
            "staffing", "recruitment", "consulting", "konsultbolag", "konsultföretag",
            "interim", "resource", "resurs", "konsultuppdrag", "konsultroll",
            "för kunds räkning", "on behalf of client", "för vår kund", "for our client"
        ]
        
        # IT and programming related keywords
        self.it_keywords = [
            "it", "data", "system", "utvecklare", "developer", "programmer", "programmerare",
            "software", "mjukvara", "web", "webb", "kod", "code", "java", "python", "c#",
            "javascript", "frontend", "backend", "fullstack", "databas", "database",
            "nätverk", "network", "säkerhet", "security", "devops", "cloud", "moln",
            "tekniker", "engineer", "ingenjör", "arkitekt", "architect", "support",
            "administration", "förvaltning", "agile", "scrum", "tech", "teknik"
        ]
    
    def is_government_job(self, job):
        """
        Check if a job is from a government organization
        
        Args:
            job (dict): Job dictionary
            
        Returns:
            bool: True if it's a government job, False otherwise
        """
        employer = job.get("employer", "").lower()
        description = job.get("description", "").lower()
        
        # Check if it's a government organization
        is_government = any(keyword in employer for keyword in self.gov_keywords)
        
        # If not found in employer name, check description
        if not is_government:
            is_government = any(keyword in description[:1000] for keyword in self.gov_keywords)
        
        return is_government
    
    def is_consultant_job(self, job):
        """
        Check if a job is a consultant position
        
        Args:
            job (dict): Job dictionary
            
        Returns:
            bool: True if it's a consultant job, False otherwise
        """
        title = job.get("title", "").lower()
        employer = job.get("employer", "").lower()
        description = job.get("description", "").lower()
        
        # Check if it's a consultant position
        is_consultant = any(keyword in title for keyword in self.consultant_keywords)
        
        # If not found in title, check employer
        if not is_consultant:
            is_consultant = any(keyword in employer for keyword in self.consultant_keywords)
        
        # If not found in employer, check description
        if not is_consultant:
            is_consultant = any(keyword in description[:1000] for keyword in self.consultant_keywords)
            
        # Additional pattern matching for consultant positions
        consultant_patterns = [
            r"konsult(uppdrag|roll)",
            r"för (vår|kunds) räkning",
            r"on behalf of (our|client)",
            r"for our client",
            r"(vår|min) kund söker",
            r"(our|my) client is looking for"
        ]
        
        if not is_consultant:
            is_consultant = any(re.search(pattern, description, re.IGNORECASE) for pattern in consultant_patterns)
        
        return is_consultant
    
    def is_it_job(self, job):
        """
        Check if a job is IT/programming related
        
        Args:
            job (dict): Job dictionary
            
        Returns:
            bool: True if it's an IT job, False otherwise
        """
        title = job.get("title", "").lower()
        description = job.get("description", "").lower()
        
        # Check if it's an IT job
        is_it = any(keyword in title for keyword in self.it_keywords)
        
        # If not found in title, check description
        if not is_it:
            is_it = any(keyword in description[:1000] for keyword in self.it_keywords)
        
        return is_it
    
    def is_in_gothenburg(self, job):
        """
        Check if a job is located in Gothenburg
        
        Args:
            job (dict): Job dictionary
            
        Returns:
            bool: True if it's in Gothenburg, False otherwise
        """
        location = job.get("location", "").lower()
        
        # Check if it's in Gothenburg
        return "göteborg" in location or "gothenburg" in location
    
    def filter_jobs(self, jobs, exclude_consultants=True, only_government=True, only_it=True, only_gothenburg=True):
        """
        Filter jobs based on various criteria
        
        Args:
            jobs (list): List of job dictionaries
            exclude_consultants (bool): Whether to exclude consultant positions
            only_government (bool): Whether to include only government jobs
            only_it (bool): Whether to include only IT jobs
            only_gothenburg (bool): Whether to include only jobs in Gothenburg
            
        Returns:
            list: Filtered list of jobs
        """
        filtered_jobs = []
        
        for job in jobs:
            # Apply filters based on parameters
            if exclude_consultants and self.is_consultant_job(job):
                continue
                
            if only_government and not self.is_government_job(job):
                continue
                
            if only_it and not self.is_it_job(job):
                continue
                
            if only_gothenburg and not self.is_in_gothenburg(job):
                continue
            
            filtered_jobs.append(job)
        
        return filtered_jobs

def main():
    """Main function to test the job filter"""
    # Determine the output directory - use current directory for GitHub Actions
    output_dir = os.getcwd()
    
    # Load jobs from JSON file
    input_file = os.path.join(output_dir, "government_it_jobs.json")
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading jobs: {e}")
        return
    
    print(f"Loaded {len(jobs)} jobs from file.")
    
    # Create filter
    job_filter = JobFilter()
    
    # Apply filters
    filtered_jobs = job_filter.filter_jobs(
        jobs, 
        exclude_consultants=True, 
        only_government=True, 
        only_it=True, 
        only_gothenburg=True
    )
    
    print(f"After filtering: {len(filtered_jobs)} jobs remain.")
    
    # Save filtered jobs to file
    output_file = os.path.join(output_dir, "filtered_jobs.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_jobs, f, ensure_ascii=False, indent=2)
    
    print(f"Filtered jobs saved to {output_file}")
    
    # Update last updated timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(output_dir, "last_updated.txt"), "w", encoding="utf-8") as f:
        f.write(timestamp)
    
    print(f"Updated last_updated.txt with timestamp: {timestamp}")
    
    # Print sample of filtered jobs
    if filtered_jobs:
        print("\nSample of filtered jobs:")
        for job in filtered_jobs[:5]:
            print(f"- {job['title']} at {job['employer']} ({job['location']})")
            print(f"  Published: {job['published']}, Deadline: {job['deadline']}")
            print(f"  URL: {job['url']}")
            print()

if __name__ == "__main__":
    main()
