from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()

# Check if the environment variables are set
if not (os.getenv("DEFAULT_MODEL") and os.getenv("BASE_URL") and os.getenv("OPENAI_API_KEY")):
    print("Warning: Environment variables not set. Using default values.")
    print("DEFAULT_MODEL:", "qwen2.5-coder:7b-instruct-fp16")
    print("BASE_URL:", "http://localhost:11434/v1")
    print("OPENAI_API_KEY:", "ollama")

# Define the settings
SYSTEM_PROMPT_PATH = "agento/system_prompt.txt"
DEFAULT_MODEL = "qwen2.5-coder:7b-instruct-fp16" # Default model for the agent
BASE_URL = os.getenv("BASE_URL") if os.getenv("BASE_URL") else "http://localhost:11434/v1" # Base URL for the OpenAI client
API_KEY = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") else "ollama" # API key for the OpenAI client