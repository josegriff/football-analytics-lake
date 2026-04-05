"""
AWS Athena database client and query functions.
"""

import streamlit as st
import pandas as pd
from pyathena import connect
from dashboard.config import APP_CONFIG


@st.cache_resource
def get_athena_connection():
    """
    Create cached Athena connection.
    
    Returns:
        pyathena.Connection: Database connection
    """
    return connect(
        s3_staging_dir=f"s3://{APP_CONFIG['s3_bucket']}/athena-results/",
        region_name=APP_CONFIG['aws_region'],
        schema_name=APP_CONFIG['athena_database']
    )


@st.cache_data(ttl=APP_CONFIG['cache_ttl'])
def execute_query(query):
    """
    Execute Athena query with caching.
    
    Args:
        query (str): SQL query
        
    Returns:
        pd.DataFrame: Query results
    """
    conn = get_athena_connection()
    return pd.read_sql(query, conn)


def load_standings():
    """
    Load latest league standings (current week only).
    
    Returns:
        pd.DataFrame: Standings data
    """
    query = """
    SELECT 
        team, position, playedGames, won, draw, lost, 
        points, goalDifference, goalsFor, goalsAgainst, year, month, week
    FROM standings
    ORDER BY year DESC, month DESC, week DESC, position ASC
    LIMIT 20
    """
    return execute_query(query)


def load_matches(limit=50):
    """
    Load recent match results.
    
    Args:
        limit (int): Number of matches to load
        
    Returns:
        pd.DataFrame: Match data
    """
    query = f"""
    SELECT 
        utcDate, homeTeam, awayTeam, homeScore, awayScore, matchday, status
    FROM matches
    WHERE status = 'FINISHED'
    ORDER BY utcDate DESC
    LIMIT {limit}
    """
    df = execute_query(query)
    df['utcDate'] = pd.to_datetime(df['utcDate'])
    return df


def get_home_away_stats():
    """
    Calculate home vs away statistics.
    
    Returns:
        pd.DataFrame: Win percentages
    """
    query = """
    SELECT 
        CASE 
            WHEN homeScore > awayScore THEN 'Home Win'
            WHEN awayScore > homeScore THEN 'Away Win'
            ELSE 'Draw'
        END AS result,
        COUNT(*) AS match_count
    FROM matches
    WHERE status = 'FINISHED'
    GROUP BY 
        CASE 
            WHEN homeScore > awayScore THEN 'Home Win'
            WHEN awayScore > homeScore THEN 'Away Win'
            ELSE 'Draw'
        END
    """
    df = execute_query(query)
    total = df['match_count'].sum()
    df['percentage'] = (df['match_count'] / total * 100).round(2)
    return df

