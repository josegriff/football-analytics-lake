import json
import boto3
import pandas as pd

BUCKET = "football-data-lake-2026"
RAW_PREFIX = "raw/standings/"
PROCESSED_KEY = "processed/standings/la_liga_standings_processed.json"

s3 = boto3.client("s3")


def list_s3_keys(bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    keys = []

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])

    return keys


def transform_standings():

    keys = list_s3_keys(BUCKET, RAW_PREFIX)

    if not keys:
        print("No raw standings files found.")
        return

    print(f"Found {len(keys)} standings files")

    all_rows = []

    for key in keys:

        obj = s3.get_object(Bucket=BUCKET, Key=key)
        data = json.loads(obj["Body"].read())

        standings = data.get("standings", [])

        if not standings:
            print(f"No standings data in {key}")
            continue

        total_table = None

        for table in standings:
            if table.get("type") == "TOTAL":
                total_table = table.get("table", [])
                break

        if not total_table:
            total_table = standings[0].get("table", [])

        for team in total_table:

            row = {
                "team": team["team"]["name"],
                "position": team["position"],
                "playedGames": team["playedGames"],
                "won": team["won"],
                "draw": team["draw"],
                "lost": team["lost"],
                "points": team["points"],
                "goalDifference": team["goalDifference"]
            }

            all_rows.append(row)

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("No data extracted.")
        return

    s3.put_object(
        Bucket=BUCKET,
        Key=PROCESSED_KEY,
        Body=df.to_json(orient="records", lines=True),
        ContentType="application/json"
    )

    print(f"Processed standings uploaded to s3://{BUCKET}/{PROCESSED_KEY}")


if __name__ == "__main__":
    transform_standings()