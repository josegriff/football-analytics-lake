from dotenv import load_dotenv
import os

load_dotenv() 
API_KEY = os.getenv("FOOTBALL_API_KEY")

if not API_KEY:
    raise ValueError("FOOTBALL_API_KEY not found in .env")