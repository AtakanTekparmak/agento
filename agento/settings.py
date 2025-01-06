from dotenv import load_dotenv
import os

# Load the environment variables from the .env file
load_dotenv()

# Provider settings
LM_STUDIO_URL = "http://localhost:1234/v1"
OLLAMA_URL = "http://localhost:11434/v1"
VLLM_URL = "http://localhost:8000/v1"
OPENROUTER_URL = "https://openrouter.ai/api/v1"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

PROVIDER_URLS = {
    "lm_studio": (LM_STUDIO_URL, ""),
    "ollama": (OLLAMA_URL, "ollama"),
    "vllm": (VLLM_URL, ""),
    "openrouter": (OPENROUTER_URL, OPENROUTER_API_KEY),
}

# Check if the environment variables are set
if not os.getenv("DEFAULT_MODEL"):
    print("Warning: Environment variables not set. Using default values.")
    print("DEFAULT_MODEL:", "Qwen/Qwen2.5-Coder-7B-Instruct")

# Define the settings
SYSTEM_PROMPT_PATH = "agento/system_prompt.txt"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct") # Default model for the agent
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "vllm") # Default provider for the agent
DEBUG = False # Whether to print debug information