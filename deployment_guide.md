# Swedish Government IT Jobs - GitHub Pages Deployment Guide

This guide will walk you through the steps to deploy your Swedish Government IT Jobs website to GitHub Pages for free permanent hosting.

## Overview

The website will be hosted at `https://jorzy.github.io/swedish-government-it-jobs/` and will automatically update daily with the latest job listings from Swedish government organizations in Gothenburg, excluding consultant positions.

## Files Included

1. `index.html` - The main website file
2. `scripts/job_scraper.py` - Script to fetch jobs from Arbetsförmedlingen's API
3. `scripts/job_filter.py` - Script to filter jobs for government positions and exclude consultants
4. `.github/workflows/update-jobs.yml` - GitHub Actions workflow for daily updates

## Deployment Steps

### 1. Create a New Repository

1. Go to [GitHub](https://github.com/) and log in to your account (username: Jorzy)
2. Click the "+" icon in the top right corner and select "New repository"
3. Enter "swedish-government-it-jobs" as the repository name
4. Make sure it's set to "Public"
5. Do not initialize with a README, .gitignore, or license
6. Click "Create repository"

### 2. Upload the Files

After creating the repository, you'll see instructions for pushing code. You can either:

#### Option A: Upload via GitHub Web Interface

1. Click on "uploading an existing file" link on the repository page
2. Upload all the files and folders from the `github_pages` directory
3. Make sure to maintain the directory structure:
   - `index.html` at the root
   - `scripts/job_scraper.py` and `scripts/job_filter.py` in the scripts folder
   - `.github/workflows/update-jobs.yml` in the .github/workflows folder

#### Option B: Use Git Command Line

If you're comfortable with Git:

```bash
# Clone the repository
git clone https://github.com/Jorzy/swedish-government-it-jobs.git
cd swedish-government-it-jobs

# Copy all files from the github_pages directory
# (Replace /path/to/github_pages with the actual path)
cp -r /path/to/github_pages/* .
cp -r /path/to/github_pages/.github .

# Add, commit, and push
git add .
git commit -m "Initial commit with job search website"
git push origin main
```

### 3. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click on "Settings" tab
3. Scroll down to the "GitHub Pages" section
4. Under "Source", select "main" branch
5. Click "Save"
6. Wait a few minutes for GitHub to build and deploy your site

### 4. Verify GitHub Actions Workflow

1. Go to the "Actions" tab in your repository
2. You should see the "Update Job Listings" workflow
3. Click on it to see details
4. You can manually trigger the workflow by clicking "Run workflow" to get initial job data

### 5. Access Your Website

After GitHub Pages is enabled and the workflow has run at least once, your website will be available at:

`https://jorzy.github.io/swedish-government-it-jobs/`

## How It Works

1. The GitHub Actions workflow runs daily at 3:00 AM UTC
2. It executes the job scraper script to fetch the latest jobs
3. Then it runs the job filter script to filter for government IT jobs in Gothenburg
4. The filtered job data is saved to JSON files
5. The website reads these JSON files to display the job listings
6. All changes are automatically committed back to the repository

## Customization

If you want to customize the website:

1. Edit `index.html` to change the design or functionality
2. Modify `scripts/job_scraper.py` to change how jobs are fetched
3. Update `scripts/job_filter.py` to adjust the filtering criteria
4. Change `.github/workflows/update-jobs.yml` to modify the update schedule

## Troubleshooting

If you encounter issues:

1. Check the "Actions" tab to see if the workflow is running successfully
2. Look at the workflow logs for any error messages
3. Ensure GitHub Pages is properly enabled in the repository settings
4. Verify that all files are in the correct locations

## Support

If you need further assistance with the deployment, please let me know!
