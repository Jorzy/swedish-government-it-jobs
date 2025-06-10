# Updated Job Search Website - Documentation

## Overview

This updated job search website provides a comprehensive platform for finding IT, AI, and meaningful jobs in both Gothenburg and Kungsbacka. The system has been enhanced to address the failing Arbetsförmedlingen API and now includes expanded job categories and locations.

## Key Features

1. **Multiple Job Categories**:
   - IT Jobs (government positions)
   - AI Jobs (all organizations)
   - Meaningful Jobs (socially impactful organizations)

2. **Multiple Locations**:
   - Gothenburg (Göteborg)
   - Kungsbacka

3. **Enhanced Filtering**:
   - Filter by job category (using tabs)
   - Filter by employer
   - Filter by location
   - Filter by active/expired status
   - Search across all fields

4. **Consultant Exclusion**:
   - All job listings automatically exclude consultant positions

5. **Automatic Updates**:
   - Daily updates via GitHub Actions
   - Manual update option

## System Components

1. **Job Scraper** (`scripts/new_sources/indeed_job_scraper.py`):
   - Replaces the failing Arbetsförmedlingen API
   - Searches for jobs across multiple categories and locations
   - Generates sample data when API access is unavailable

2. **Website Interface** (`index.html`):
   - Tabbed interface for different job categories
   - Responsive design for all devices
   - Advanced filtering options

3. **GitHub Actions Workflow** (`.github/workflows/update-jobs.yml`):
   - Runs the job scraper daily
   - Updates job listings automatically
   - Can be triggered manually

## Installation and Setup

1. **GitHub Repository Setup**:
   - Upload all files to your GitHub repository
   - Ensure the repository structure matches the provided files
   - Make sure the `.github/workflows` directory is properly uploaded

2. **GitHub Pages Configuration**:
   - Enable GitHub Pages in your repository settings
   - Set the source to the main branch

3. **API Key (Optional)**:
   - If you want to use the actual Indeed API instead of sample data, obtain an API key from RapidAPI
   - Update the `RAPIDAPI_KEY` variable in `scripts/new_sources/indeed_job_scraper.py`

## Usage

1. **Viewing Jobs**:
   - Navigate to the website
   - Use the tabs to switch between job categories
   - Use the filters to narrow down results

2. **Updating Jobs**:
   - Jobs are updated automatically every day at 3:00 AM UTC
   - Click the "Update Now" button for immediate updates
   - Alternatively, manually trigger the GitHub Actions workflow

## Troubleshooting

1. **No Jobs Displayed**:
   - Check if the JSON files exist in your repository
   - Verify that the GitHub Actions workflow is running correctly
   - Check for any error messages in the GitHub Actions logs

2. **GitHub Actions Failures**:
   - Ensure the repository has the correct permissions set
   - Check that the workflow file is properly formatted
   - Verify that the Python dependencies are installed correctly

## Future Enhancements

1. **Real API Integration**:
   - Replace sample data with actual API data when available
   - Add more job sources for comprehensive coverage

2. **Email Notifications**:
   - Add option for email notifications when new jobs are posted

3. **User Accounts**:
   - Allow users to save favorite jobs
   - Provide personalized job recommendations

## Contact

For any issues or suggestions, please open an issue on the GitHub repository.
