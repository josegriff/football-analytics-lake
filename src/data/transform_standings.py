"""
Transform raw standings JSON into processed NDJSON format for Athena.

This script:
1. Downloads the latest raw standings file from S3
2. Flattens and extracts key fields
3. Uploads as newline-delimited JSON (NDJSON) to processed/ folder
"""

import boto3
import json
import pandas as pd
from datetime import datetime
import logging

BUCKET_NAME = "football-data-lake-2026"
s3 = boto3.client('s3')

# Configure logging
logging.basicConfig(level=logging.WARNING)


def get_latest_raw_standings():
    """Get the most recent raw standings file from S3"""
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix='raw/standings/'
    )
    
    if 'Contents' not in response:
        raise FileNotFoundError("No raw standings files found")
    
    # Sort by 'LastModified' and get the newest
    latest = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)[0]
    key = latest['Key']
    
    print(f"Reading: s3://{BUCKET_NAME}/{key}")
    
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    data = json.loads(obj['Body'].read())
    
    return data


def parse_goals(goals_string):
    """Safely parse goals string into (goals_for, goals_against)"""
    
    if not goals_string or not isinstance(goals_string, str):
        return 0, 0
    
    # Normalize common formatting issues
    cleaned = goals_string.strip().replace(" ", "").replace("-", ":")
    parts = cleaned.split(":")
    
    try:
        if len(parts) >= 2:
            return int(parts[0]), int(parts[1])
    except ValueError:
        logging.warning(f"Invalid goals format encountered: {goals_string}")
    
    # Fallback if parsing fails
    return 0, 0


def transform_standings(raw_data):
    """Extract standings table from raw API response"""
    
    standings_list = raw_data.get('standings', [])
    
    if not standings_list:
        raise ValueError("No standings data found in raw file")
    
    table = standings_list[0].get('table', [])
    
    # Debug: Print first entry to see available fields
    if table:
        print("Available fields in first entry:")
        for key, value in table[0].items():
            print(f"  {key}: {value}")
    
    records = []
    for entry in table:
        # Use the actual goalsFor and goalsAgainst fields from API
        goals_for = entry.get('goalsFor', 0)
        goals_against = entry.get('goalsAgainst', 0)
        
        # Calculate goalDifference from goalsFor and goalsAgainst
        calculated_goal_difference = goals_for - goals_against
        
        records.append({
            'team': entry['team']['name'],
            'position': entry['position'],
            'playedGames': entry['playedGames'],
            'won': entry['won'],
            'draw': entry['draw'],
            'lost': entry['lost'],
            'points': entry['points'],
            'goalDifference': calculated_goal_difference,  # Use calculated value
            'goalsFor': goals_for,
    'goalsAgainst': goals_against
        })
    
    return pd.DataFrame(records)


def upload_processed_standings(df):
    """Upload processed standings as NDJSON to S3 with partitioning"""
    
    # Convert to NDJSON (newline-delimited JSON)
    ndjson = df.to_json(orient='records', lines=True)
    
    # Get current date for partitioning
    now = datetime.now()
    
    # ISO calendar for consistent weekly partitioning
    iso_calendar = now.isocalendar()
    year = iso_calendar[0]
    week = iso_calendar[1]
    
    # Partitioned S3 path
    s3_key = f"processed/standings/year={year}/month={now.month:02d}/week={week:02d}/standings.json"
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=ndjson,
        ContentType='application/json'
    )
    
    print(f"Uploaded: s3://{BUCKET_NAME}/{s3_key}")
    print(f"Partition: Year={year}, Month={now.month:02d}, Week={week:02d}")
    print(f"Records: {len(df)}")


def main():
    print("=" * 60)
    print("STANDINGS TRANSFORMATION")
    print("=" * 60)
    
    # Step 1: Download latest raw data
    raw_data = get_latest_raw_standings()
    
    # Step 2: Transform
    df = transform_standings(raw_data)
    print(f"\nExtracted {len(df)} teams")
    print("\nPreview:")
    print(df.head())
    
    # Step 3: Upload processed data
    upload_processed_standings(df)
    
    print("\n" + "=" * 60)
    print("TRANSFORMATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()