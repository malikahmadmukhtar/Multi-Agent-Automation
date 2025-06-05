import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from config.settings import temperature, active_model, groq_api_key


def get_llm():
    """Initializes and returns the Gemini LLM."""
    try:
        llm = ChatGroq(
            temperature=temperature,
            model=active_model,
            api_key=groq_api_key
        )
        # llm = ChatGoogleGenerativeAI(
        #     model="gemini-2.0-flash",
        #     temperature=0.1,
        #     google_api_key=os.getenv("GEMINI_API_KEY")
        # )
        print("LLM initialized successfully.")
        return llm
    except Exception as e:
        print(f"Error initializing LLM. Make sure API key is set: {e}")
        return None