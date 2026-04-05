"""
Constants and utility configurations for the data pipeline.
"""

# AWS CONFIGURATION
AWS_CONFIG = {
    'bucket_name': 'football-data-lake-2026',
    'region': 'us-east-1',
    'athena_database': 'football_analytics',
    'athena_output_location': 's3://football-data-lake-2026/athena-results/'
}

# API CONFIGURATION
API_CONFIG = {
    'base_url': 'https://api.football-data.org/v4',
    'headers_template': {
        'X-Auth-Token': None  # Set from environment variable
    },
    'endpoints': {
        'la_liga_matches': 'competitions/PD/matches',
        'la_liga_standings': 'competitions/PD/standings',
        'all_matches': 'matches'
    }
}

# S3 PATH TEMPLATES
S3_PATHS = {
    'raw': {
        'matches': 'raw/matches/',
        'standings': 'raw/standings/'
    },
    'processed': {
        'matches': 'processed/matches/',
        'standings': 'processed/standings/'
    }
}

# DATA SCHEMAS
STANDINGS_SCHEMA = [
    'team',
    'position',
    'playedGames',
    'won',
    'draw',
    'lost',
    'points',
    'goalDifference',
    'goalsFor',
    'goalsAgainst',
    'year',
    'month',
    'week'
]

MATCHES_SCHEMA = [
    'utcDate',
    'homeTeam',
    'awayTeam',
    'homeScore',
    'awayScore',
    'matchday',
    'status'
]

# COMPETITION ZONES (for table classification)
LEAGUE_ZONES = {
    'champions_league': {
        'name': 'UEFA Champions League',
        'positions': [1, 2, 3, 4],
        'color': '#0066CC'
    },
    'europa_league': {
        'name': 'UEFA Europa League',
        'positions': [5, 6, 7],
        'color': '#FF6600'
    },
    'relegation': {
        'name': 'Relegation to Segunda División',
        'positions': [18, 19, 20],
        'color': '#CC0000'
    }
}

# CACHE SETTINGS
CACHE_CONFIG = {
    'ttl_seconds': 3600,  # 1 hour
    'max_age': 86400      # 24 hours
}

# LOGGING CONFIGURATION
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

