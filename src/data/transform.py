"""
Transform raw matches JSON into processed NDJSON format for Athena.

This script:
1. Downloads the latest raw matches file from S3
2. Flattens and extracts key fields
3. Uploads as newline-delimited JSON (NDJSON) to processed/ folder
"""

import boto3
import json
import pandas as pd
from datetime import datetime

BUCKET_NAME = "football-data-lake-2026"
s3 = boto3.client('s3')

def get_latest_raw_matches():
    """Get the most recent raw matches file from S3"""
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix='raw/matches/'
    )
    
    if 'Contents' not in response:
        raise FileNotFoundError("No raw matches files found")
    
    # Sort by 'LastModified' and get the newest
    latest = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)[0]
    key = latest['Key']
    
    print(f"Reading: s3://{BUCKET_NAME}/{key}")
    
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    data = json.loads(obj['Body'].read())
    
    return data

def transform_matches(raw_data):
    """Extract matches table from raw API response"""
    
    # Navigate the API structure
    # Typical structure: {"matches": [...]}
    matches_list = raw_data.get('matches', [])
    
    if not matches_list:
        raise ValueError("No matches data found in raw file")
    
    # Flatten into records
    records = []
    for match in matches_list:
        # Only include finished matches with scores
        if match.get('status') == 'FINISHED' and match.get('score'):
            records.append({
                'utcDate': match['utcDate'],
                'homeTeam': match['homeTeam']['name'],
                'awayTeam': match['awayTeam']['name'],
                'homeScore': match['score']['fullTime']['home'],
                'awayScore': match['score']['fullTime']['away'],
                'matchday': match.get('matchday'),
                'status': match['status']
            })
    
    return pd.DataFrame(records)

def upload_processed_matches(df):
    """Upload processed matches as NDJSON to S3 with partitioning"""
    
    # Convert to NDJSON (newline-delimited JSON)
    # Each record on its own line, no array wrapper
    ndjson = df.to_json(orient='records', lines=True)
    
    # Get current date for partitioning
    now = datetime.now()
    
    # Calculate ISO week number (1-53)
    # Week 1 is the first week with a Thursday in the new year
    iso_calendar = now.isocalendar()
    year = iso_calendar[0]   # ISO year (might differ from calendar year in Jan/Dec)
    week = iso_calendar[1]   # ISO week number (1-53)
    
    # Create partitioned path structure
    # Format: processed/matches/year=2026/month=03/week=12/matches.json
    s3_key = f"processed/matches/year={year}/month={now.month:02d}/week={week:02d}/matches.json"
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=ndjson,
        ContentType='application/json'
    )
    
    print(f" Uploaded: s3://{BUCKET_NAME}/{s3_key}")
    print(f" Partition: Year={year}, Month={now.month:02d}, Week={week:02d}")
    print(f" Records: {len(df)}")

def main():
    print("=" * 60)
    print("MATCHES TRANSFORMATION")
    print("=" * 60)
    
    # Step 1: Download latest raw data
    raw_data = get_latest_raw_matches()
    
    # Step 2: Transform
    df = transform_matches(raw_data)
    print(f"\nExtracted {len(df)} finished matches")
    print("\nPreview:")
    print(df.head())
    
    # Step 3: Upload processed data
    upload_processed_matches(df)
    
    print("\n" + "=" * 60)
    print("TRANSFORMATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()