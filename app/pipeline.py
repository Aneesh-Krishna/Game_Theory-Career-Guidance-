# app/pipeline.py

from agents.career_agent import handle_user_input
from tools.linkedin_api import fetch_linkedin_profile
from tools.rapidapi_jobs import search_jobs
from tools.web_search_tool import perform_web_search
from game_theory.career_game_model import explain_game_theory_choice
from utils.db_handler import save_session, load_session

def is_input_complete(user_input: str, known_data: dict) -> bool:
    """
    Basic completeness check. Can be enhanced with LLM.
    """
    required = ["education", "skills", "interests"]
    return all(k in known_data and known_data[k] for k in required)

def fetch_job_data(query: str):
    """
    Try LinkedIn first → fallback to RapidAPI → fallback to Web.
    """
    result = fetch_linkedin_profile(query)
    if isinstance(result, str) and "error" in result.lower():
        result = search_jobs(query)
    if isinstance(result, str) and "error" in result.lower():
        result = perform_web_search(f"career scope of {query}")
    return result

def run_pipeline(user_id: str, user_input: str, known_data: dict = {}):
    """
    Full pipeline orchestration.
    """
    session_data = load_session(user_id)

    # Step 1: Check input completeness
    complete = is_input_complete(user_input, known_data)

    if not complete:
        return {
            "status": "incomplete",
            "message": "Please provide more information: education, skills, and interests."
        }

    # Step 2: Query LLM agent for response
    agent_response = handle_user_input(user_input)

    # Step 3: Fetch job market data
    job_data = fetch_job_data(user_input)

    # Step 4: Game-theory analysis
    game_explanation = explain_game_theory_choice()

    # Step 5: Save session
    session_data["last_input"] = user_input
    session_data["agent_response"] = agent_response
    session_data["job_data"] = job_data
    session_data["game_explanation"] = game_explanation
    save_session(user_id, session_data)

    # Step 6: Return structured result
    return {
        "status": "success",
        "recommendation": agent_response,
        "job_data": job_data,
        "game_theory": game_explanation
    }
