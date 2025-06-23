# app/tools/web_search_tool.py

import os
from dotenv import load_dotenv

from langchain.tools.tavily_search import TavilySearchResults

load_dotenv()

# Load Tavily API Key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize the tool
search_tool = TavilySearchResults(api_key=TAVILY_API_KEY)

def perform_web_search(query: str, num_results: int = 3):
    """
    Use TavilySearchResults to fetch fallback web info.
    """
    try:
        results = search_tool.run(query=query, num_results=num_results)

        summaries = []
        for result in results:
            summaries.append(f"- {result['title']}: {result['url']}\n  {result['content'][:200]}...")

        return "\n\n".join(summaries) if summaries else "No relevant web results found."
    except Exception as e:
        return f"Web search error: {str(e)}"
