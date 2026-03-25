import json
import boto3
import pandas as pd

BUCKET = "football-data-lake-2026"
RAW_PREFIX = "raw/matches/"
PROCESSED_PREFIX = "processed/matches/"
s3 = boto3.client("s3")

def list_s3_keys(bucket, prefix):
    """Return list of object keys under a prefix"""
    keys = []
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for obj in resp.get("Contents", []):
        keys.append(obj["Key"])
    return keys

def fetch_json_from_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(obj["Body"].read())

def transform_matches():
    keys = list_s3_keys(BUCKET, RAW_PREFIX)
    all_matches = []

    for key in keys:
        data = fetch_json_from_s3(BUCKET, key)
        for match in data.get("matches", []):
            all_matches.append({
                "utcDate": match.get("utcDate"),
                "homeTeam": match.get("homeTeam", {}).get("name"),
                "awayTeam": match.get("awayTeam", {}).get("name"),
                "homeScore": match.get("score", {}).get("fullTime", {}).get("home"),
                "awayScore": match.get("score", {}).get("fullTime", {}).get("away")
            })

    df = pd.DataFrame(all_matches)
    
    processed_key = f"{PROCESSED_PREFIX}la_liga_matches_processed.json"
    
    s3.put_object(
        Bucket=BUCKET, 
        Key=processed_key, 
        Body=df.to_json(orient="records", lines=True))
    print(f"Processed data uploaded to s3://{BUCKET}/{processed_key}")

if __name__ == "__main__":
    transform_matches()