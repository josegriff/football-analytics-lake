from dotenv import load_dotenv
import os
import requests
import json
import boto3
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("FOOTBALL_API_KEY")
BUCKET_NAME = "football-data-lake-2026"

if not API_KEY:
    raise ValueError("FOOTBALL_API_KEY not set")

HEADERS = {"X-Auth-Token": API_KEY}
s3 = boto3.client("s3")

def fetch_and_upload(endpoint, prefix):
    url = f"https://api.football-data.org/v4/{endpoint}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Error {resp.status_code} on {endpoint}")
        return

    data = resp.json()
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    folder = "matches" if "matches" in prefix.lower() else "standings"
    s3_key = f"raw/{folder}/{prefix}_{now}.json"

    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(data, indent=2),
            ContentType="application/json"
        )
        print(f"Uploaded: s3://{BUCKET_NAME}/{s3_key}")
    except Exception as e:
        print(f"S3 Upload failed: {e}")

# List of endpoints to fetch
endpoints = [
    ("competitions/PD/matches", "la_liga_matches"),
    ("competitions/PD/standings", "la_liga_standings")
]

for ep, prefix in endpoints:
    fetch_and_upload(ep, prefix)