import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = ""

# API configuration
API_ENDPOINT = "http://localhost:5000/extract"

# Output file configuration
OUTPUT_CSV_FILE = "output.csv" 