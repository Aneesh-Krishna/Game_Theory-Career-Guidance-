# app/tools/rapidapi_jobs.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def search_jobs(query: str) -> str:
    """
    Uses a RapidAPI job listing service like JSearch.
    """
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": query,
        "num_pages": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()

        jobs = []
        for job in data.get("data", [])[:5]:  # Limit to 5
            jobs.append({
                "title": job.get("job_title"),
                "company": job.get("employer_name"),
                "location": job.get("job_city"),
                "salary": job.get("job_min_salary", "N/A"),
                "description": job.get("job_description", "")[:200] + "...",
                "skills": job.get("job_required_skills", []) or ["N/A"]
            })

        return jobs if jobs else "No jobs found on RapidAPI."
    except Exception as e:
        return f"RapidAPI Job error: {str(e)}"
