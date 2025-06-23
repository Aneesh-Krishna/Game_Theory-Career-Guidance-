# app/tools/linkedin_api.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_API_TOKEN = os.getenv("LINKEDIN_API_TOKEN")

def fetch_linkedin_profile(query: str) -> str:
    """
    Simulated placeholder for DMA-based LinkedIn API (example only).
    Replace with actual API endpoint & parsing if you have access.
    """
    headers = {
        "Authorization": f"Bearer {LINKEDIN_API_TOKEN}",
        "Accept": "application/json"
    }

    url = f"https://api.linkedin.com/v2/jobSearch?q={query}&location=India"  # Example format
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        jobs = []
        for job in data.get("jobs", [])[:5]:  # Limit to 5 results
            jobs.append({
                "title": job.get("title"),
                "location": job.get("location"),
                "company": job.get("company"),
                "salary": job.get("estimatedSalary", "N/A"),
                "skills": job.get("skills", []),
                "description": job.get("description", "")[:200] + "..."
            })

        return jobs if jobs else "No LinkedIn jobs found."
    except Exception as e:
        return f"LinkedIn API error: {str(e)}"
