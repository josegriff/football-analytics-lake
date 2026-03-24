"""

This script is designed for extracting football data from the football-data.org API 
and loading it into an AWS S3 bucket as raw JSON files.

Dependencies:
- boto3: AWS SDK for Python, used for interacting with S3.
- requests: Used for making HTTP requests to the football-data.org API.
- dotenv: Used for loading environment variables from a .env file.

"""

from dotenv import load_dotenv
import os
import requests
import json
import boto3
from datetime import datetime


# Access API key
load_dotenv() 
API_KEY = os.getenv("FOOTBALL_API_KEY")

if not API_KEY:
    raise ValueError("FOOTBALL_API_KEY not found in .env")


# Set up S3 info and client
BUCKET_NAME = "football-data-lake-2026"
HEADERS = {"X-Auth-Token": API_KEY}

s3 = boto3.client('s3')


# Define the Fetch and Upload Function
def fetch_and_upload(endpoint, filename_prefix):
    url = f"https://api.football-data.org/v4/{endpoint}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return


# Parse JSON data
    data = response.json()
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    s3_key = f"raw/{filename_prefix}_{now}.json"


# Upload to S3
    s3.put_object(
        Bucket = BUCKET_NAME,
        Key = s3_key,
        Body = json.dumps(data, indent=2),
        ContentType = "application/json"
    )
    
    print(f"Uploaded to s3://{BUCKET_NAME}/{s3_key}")


# Test calls to fetch and upload data
fetch_and_upload("matches", "la_liga_matches")
fetch_and_upload("competitions/PD/matches", "la_liga_matches")
fetch_and_upload("competitions/PD/standings", "la_liga_standings")