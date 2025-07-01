# Job Search Project Documentation

## Project Overview

This project creates a website that displays IT, AI, and RPA job listings in Gothenburg and Kungsbacka, Sweden. The system:

1. Excludes consultant positions
2. Highlights meaningful employers
3. Provides filtering by job type, location, and relevance
4. Updates automatically daily via GitHub Actions
5. Allows manual updates through GitHub's workflow_dispatch feature

## Essential Files

These files are required for the project to function properly:

- `index.html` - The main website interface
- `scripts/jobtech_job_scraper_enhanced.py` - The enhanced job scraper with improved filtering
- `.github/workflows/update-jobs.yml` - GitHub Actions workflow for automatic updates
- `data/` directory containing:
  - `it_jobs.json` - IT job listings
  - `ai_jobs.json` - AI job listings
  - `rpa_jobs.json` - RPA job listings
  - `all_jobs.json` - Combined job listings
  - `last_updated.txt` - Timestamp of last update

## Files That Can Be Safely Removed

These files are no longer needed and can be safely removed:

- Any older versions of scrapers (job_scraper.py, ai_job_scraper.py, etc.)
- Any backup or test files
- Any duplicate JSON files or older versions
- Any React conversion files or other experimental code

## How to Update Job Listings

### Automatic Updates
The job listings are automatically updated daily at 3:00 AM UTC via GitHub Actions.

### Manual Updates
To manually update the job listings:

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. Select the "Update Job Listings" workflow
4. Click the "Run workflow" button
5. Wait for the workflow to complete (usually takes 1-2 minutes)

The website's "Update now" button provides a visual simulation but does not actually trigger an update. This is because GitHub Pages is a static hosting service that cannot run server-side code.

## Improvements Made

### 1. Fixed GitHub Actions Workflow
- Updated to use newer versions of GitHub Actions
- Added missing dependencies
- Ensured it calls the correct script

### 2. Enhanced RPA and Consultant Filtering
- Added stronger UiPath-related keywords
- Improved consultant detection with contextual patterns
- Added exclusion patterns for academic positions
- Implemented more sophisticated relevance scoring

### 3. Updated Website Interface
- Added clear instructions for manual updates
- Improved job card display with relevance indicators
- Added special handling for empty categories
- Enhanced filtering options

## Troubleshooting

If job listings are not updating:

1. Check the GitHub Actions logs for errors
2. Verify that the workflow has the necessary permissions
3. Ensure the script paths in the workflow file match your repository structure
4. Check that the JSON files are being properly generated and committed

If filtering is not working correctly:

1. Review the filtering logic in `jobtech_job_scraper_enhanced.py`
2. Adjust the keyword lists and relevance thresholds as needed
3. Test with different search terms and locations

## Future Enhancements

Potential improvements for the future:

1. Add email notifications for new job listings
2. Implement more advanced filtering options
3. Add visualization of job trends over time
4. Expand to additional locations or job categories
