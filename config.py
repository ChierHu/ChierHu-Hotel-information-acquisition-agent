import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#parallel tasks workers count
MAX_WORKERS = 4

# OpenAI API configuration
# BASEURL="https://api.openai.com/v1"
OPENAI_API_KEY = ""
BASEURL="https://api.openai.com/v1"

# API configuration
API_ENDPOINT = "http://localhost:5000/extract"
SCRAPER_ENDPOINT = "http://localhost:5555/extract"

# Output file configuration
OUTPUT_CSV_FILE = "output.csv" 