import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_BASE_URL = "https://models.github.ai/inference"
    MODEL_NAME = "gpt-4o" 
    TEMPERATURE = 0.2     