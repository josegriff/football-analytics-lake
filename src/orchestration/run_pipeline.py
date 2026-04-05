"""
Master pipeline orchestrator - runs the full data pipeline in sequence.

Usage:
    python run_pipeline.py
"""

import subprocess
import sys
from datetime import datetime

def print_header(message):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70 + "\n")

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    print_header(f"STEP: {description}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings:", result.stderr)
        
        print(f"{description} completed successfully\n")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"{description} FAILED\n")
        print("Error output:")
        print(e.stderr)
        return False

def main():
    """Run the complete pipeline"""
    start_time = datetime.now()
    
    print_header("FOOTBALL ANALYTICS PIPELINE - STARTED")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Define pipeline steps
    steps = [
        ("src/data/ingest_football.py", "Data Ingestion (API → S3 Raw)"),
        ("src/data/transform.py", "Transform Matches (Raw → Processed)"),
        ("src/data/transform_standings.py", "Transform Standings (Raw → Processed)")
    ]
    
    # Execute pipeline
    success_count = 0
    for script, description in steps:
        if run_script(script, description):
            success_count += 1
        else:
            print(f"\n  Pipeline stopped at: {description}")
            print("Fix the error and run again.\n")
            sys.exit(1)
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_header("PIPELINE COMPLETE")
    print(f"All {success_count}/{len(steps)} steps completed successfully")
    print(f"Duration: {duration:.2f} seconds")
    print(f"\nNext steps:")
    print("  1. Go to AWS Athena")
    print("  2. Run your analytics queries")
    print("  3. Query the 'matches' and 'standings' tables\n")

if __name__ == "__main__":
    main()