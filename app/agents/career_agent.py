# app/agents/career_agent.py

import os
import json
import re
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv

from langchain.chat_models import azure_openai
from langchain_openai import AzureChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate

load_dotenv()

# Enhanced scoring criteria for career evaluation
CAREER_SCORING_CRITERIA = {
    "salary_potential": "Expected salary range and earning potential (1-10 scale)",
    "job_security": "Stability and job security in the field (1-10 scale)", 
    "growth_opportunity": "Career advancement and professional growth potential (1-10 scale)",
    "work_life_balance": "Work-life balance and stress levels (1-10 scale)",
    "skill_transferability": "How transferable skills are to other roles/industries (1-10 scale)",
    "market_demand": "Current and future market demand for this role (1-10 scale)",
    "education_barrier": "Ease of entry and educational requirements (1-10 scale, higher = easier)",
    "remote_flexibility": "Ability to work remotely or flexibility options (1-10 scale)"
}

# Career evaluation prompt template
CAREER_EVALUATION_PROMPT = """
You are an expert career counselor with deep knowledge of job markets, salary trends, and career development. 

Your task is to analyze career options and provide structured scoring data.

IMPORTANT: Always end your response with a CAREER_MATRIX section in the exact format shown below.

User Query: {user_input}

Please provide:
1. A detailed career analysis addressing the user's specific question
2. Consider current market trends, salary data, growth prospects, and skill requirements
3. Provide personalized recommendations based on the user's situation

CAREER_MATRIX:
```json
{{
    "careers": {{
        "Career Name 1": {{
            "salary_potential": score_1_to_10,
            "job_security": score_1_to_10,
            "growth_opportunity": score_1_to_10,
            "work_life_balance": score_1_to_10,
            "skill_transferability": score_1_to_10,
            "market_demand": score_1_to_10,
            "education_barrier": score_1_to_10,
            "remote_flexibility": score_1_to_10
        }},
        "Career Name 2": {{
            "salary_potential": score_1_to_10,
            "job_security": score_1_to_10,
            "growth_opportunity": score_1_to_10,
            "work_life_balance": score_1_to_10,
            "skill_transferability": score_1_to_10,
            "market_demand": score_1_to_10,
            "education_barrier": score_1_to_10,
            "remote_flexibility": score_1_to_10
        }}
    }},
    "criteria_weights": {{
        "salary_potential": 0.15,
        "job_security": 0.15,
        "growth_opportunity": 0.15,
        "work_life_balance": 0.10,
        "skill_transferability": 0.10,
        "market_demand": 0.15,
        "education_barrier": 0.10,
        "remote_flexibility": 0.10
    }}
}}
```

Make sure to include at least 3-5 relevant career options in your analysis.
"""

# 1. Initialize the LLM
llm = AzureChatOpenAI(temperature=0.4, model="gpt-4o-mini", model_kwargs={"top_p": 0.9})

# 2. Setup memory to retain conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 3. Define tools
from tools.linkedin_api import fetch_linkedin_profile
from tools.rapidapi_jobs import search_jobs
from tools.web_search_tool import perform_web_search

tools = [
    Tool(
        name="LinkedIn lookup",
        func=fetch_linkedin_profile,
        description="Useful for retrieving career info based on LinkedIn user ID or public URL."
    ), 
    Tool(
        name="Job Market Search",
        func=search_jobs,
        description="Useful for searching job opportunities using keywords or roles."
    ), 
    Tool(
        name="Web Search",
        func=perform_web_search,
        description="Use this to fetch latest news, job trends, or salary data when other tools fail."
    )
]

# 4. Initialize Agent with tools and memory
career_agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

def extract_career_matrix_from_response(response: str) -> Optional[Dict]:
    """
    Extract career matrix from agent response
    
    Args:
        response: Agent response containing career matrix
        
    Returns:
        Dictionary with career matrix data or None if not found
    """
    try:
        # Look for CAREER_MATRIX section
        matrix_match = re.search(r'CAREER_MATRIX:\s*```json\s*(.*?)\s*```', response, re.DOTALL | re.IGNORECASE)
        
        if matrix_match:
            json_str = matrix_match.group(1)
            career_data = json.loads(json_str)
            return career_data
        
        # Fallback: look for any JSON structure
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            career_data = json.loads(json_str)
            if 'careers' in career_data:
                return career_data
        
        return None
        
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing career matrix: {e}")
        return None

def format_career_matrix_for_game_theory(career_data: Dict) -> Tuple[Dict[str, List[float]], List[str]]:
    """
    Convert career matrix data to game theory format
    
    Args:
        career_data: Structured career data from agent
        
    Returns:
        Tuple of (career_matrix, criteria_labels)
    """
    if not career_data or 'careers' not in career_data:
        return None, None
    
    careers = career_data['careers']
    criteria_order = list(CAREER_SCORING_CRITERIA.keys())
    
    # Create matrix in game theory format
    game_theory_matrix = {}
    
    for career_name, scores in careers.items():
        score_vector = []
        for criterion in criteria_order:
            score_vector.append(scores.get(criterion, 5))  # Default to 5 if missing
        game_theory_matrix[career_name] = score_vector
    
    criteria_labels = [criterion.replace('_', ' ').title() for criterion in criteria_order]
    
    return game_theory_matrix, criteria_labels

def enhance_response_with_structured_analysis(user_input: str) -> str:
    """
    Get enhanced career analysis with structured data
    
    Args:
        user_input: User's career question
        
    Returns:
        Enhanced response with career matrix
    """
    try:
        # Create enhanced prompt
        enhanced_prompt = CAREER_EVALUATION_PROMPT.format(user_input=user_input)
        
        # Get response from LLM
        response = llm([HumanMessage(content=enhanced_prompt)])
        
        return response.content
        
    except Exception as e:
        return f"Error in enhanced analysis: {str(e)}"

# 5. Enhanced wrapper to handle user input with structured output
def handle_user_input(user_input: str) -> Dict:
    """
    Enhanced handler that returns both text response and structured career data
    
    Args:
        user_input: User's career question
        
    Returns:
        Dictionary with 'response', 'career_matrix', and 'criteria_labels'
    """
    try:
        # First, get regular agent response
        agent_response = career_agent_executor.run(user_input)
        
        # Then get enhanced structured analysis
        enhanced_response = enhance_response_with_structured_analysis(user_input)
        
        # Extract career matrix
        career_data = extract_career_matrix_from_response(enhanced_response)
        
        if career_data:
            # Convert to game theory format
            career_matrix, criteria_labels = format_career_matrix_for_game_theory(career_data)
            
            # Combine responses
            combined_response = f"{agent_response}\n\n--- Enhanced Analysis ---\n{enhanced_response}"
            
            return {
                'response': combined_response,
                'career_matrix': career_matrix,
                'criteria_labels': criteria_labels,
                'raw_career_data': career_data
            }
        else:
            # Fallback if no structured data found
            return {
                'response': agent_response,
                'career_matrix': None,
                'criteria_labels': None,
                'raw_career_data': None
            }
            
    except Exception as e:
        return {
            'response': f"Error during agent execution: {str(e)}",
            'career_matrix': None,
            'criteria_labels': None,
            'raw_career_data': None
        }

# Legacy function for backward compatibility
def handle_user_input_legacy(user_input: str) -> str:
    """
    Legacy function that returns only text response
    """
    result = handle_user_input(user_input)
    return result['response']

def get_career_recommendations_for_profile(profile_data: Dict) -> Dict:
    """
    Get career recommendations based on user profile
    
    Args:
        profile_data: Dictionary with user's background info
        
    Returns:
        Structured career recommendations
    """
    
    # Build profile summary
    profile_summary = []
    if 'education' in profile_data:
        profile_summary.append(f"Education: {profile_data['education']}")
    if 'experience' in profile_data:
        profile_summary.append(f"Experience: {profile_data['experience']}")
    if 'skills' in profile_data:
        profile_summary.append(f"Skills: {profile_data['skills']}")
    if 'interests' in profile_data:
        profile_summary.append(f"Interests: {profile_data['interests']}")
    
    profile_text = "; ".join(profile_summary)
    
    query = f"Based on this profile: {profile_text}, what are the best career options and how do they compare?"
    
    return handle_user_input(query)

# Testing function
def test_career_agent():
    """Test the enhanced career agent"""
    
    test_queries = [
        "Should I pursue Data Science or Product Management?",
        "I'm a software engineer with 3 years experience. What are my best career options?",
        "What's better: MBA or staying technical as a senior engineer?"
    ]
    
    for query in test_queries:
        print(f"\n=== Testing Query: {query} ===")
        result = handle_user_input(query)
        
        print("Response:", result['response'][:200] + "...")
        if result['career_matrix']:
            print("Career Matrix Keys:", list(result['career_matrix'].keys()))
            print("Criteria Labels:", result['criteria_labels'])
        else:
            print("No structured career matrix found")

if __name__ == "__main__":
    test_career_agent()