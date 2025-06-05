import os
from dotenv import load_dotenv

load_dotenv()

## LLM to use
active_model = 'deepseek-r1-distill-llama-70b'
# active_model = 'meta-llama/llama-4-scout-17b-16e-instruct'
# active_model = 'meta-llama/llama-4-maverick-17b-128e-instruct'
# active_model = 'qwen-qwq-32b'
# active_model = 'llama-3.3-70b-versatile'

## model temperature
temperature = 0.3

## max context to send
MAX_PREVIOUS_MESSAGES_FOR_CONTEXT = 20

## groq api setup
groq_api_key = os.getenv("GROQ_API_KEY")

## tavily api setup
tavily_api_key = os.getenv("TAVILY_API_KEY")

## weather api setup
weather_api_key = os.getenv("OPEN_WEATHER_KEY")

## google scopes
GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]

## assets
project_root = os.getcwd()
meta_image = os.path.join(project_root, "assets", "images", "meta.png")
agent_image = os.path.join(project_root, "assets", "images", "agent.png")
user_image = os.path.join(project_root, "assets", "images", "user.png")
