from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from config.settings import tavily_api_key
import streamlit as st

# Instantiate Tavily tool once (reuse for efficiency)
tavily = TavilySearchResults(k=5, tavily_api_key=tavily_api_key)  # Adjust `k` to control how many results to fetch

@tool
def tavily_web_search_tool(query: str) -> str:
    """
    Uses Tavily to perform a web search and return summarized results.
    Use this tool for any question that you don't have info about.
    You can get any info from this tool using web like searching weather other than the current weather or a product or a service.

    Args:
        query (str): The user's search query.

    Returns:
        str: Search results as a summary.
    """
    st.sidebar.info("Used web search tool")

    print("🔍 Running Tavily web search tool...")
    print(f"📋 Query: {query}")

    if not query.strip():
        print("Empty query")
        return "Error: Search query is required."

    try:
        results = tavily.run(query)
        print("Tavily search completed")
        return results
    except Exception as e:
        print(f"Tavily search failed: {str(e)}")
        return f"Error during Tavily search: {str(e)}"
