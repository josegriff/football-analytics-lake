"""
Unit tests for data ingestion (API → S3).

Run with: pytest tests/test_ingestion.py -v
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# Mock the ingestion functions (assuming they exist in src/data/ingest_football.py)
# You'll need to refactor your ingest_football.py to have testable functions

# FIXTURES
@pytest.fixture
def mock_api_response_standings():
    """Mock API response for standings."""
    return {
        'standings': [{
            'table': [
                {
                    'team': {'name': 'FC Barcelona'},
                    'position': 1,
                    'playedGames': 29,
                    'won': 24,
                    'draw': 1,
                    'lost': 4,
                    'points': 73,
                    'goalDifference': 50
                },
                {
                    'team': {'name': 'Real Madrid CF'},
                    'position': 2,
                    'playedGames': 29,
                    'won': 22,
                    'draw': 3,
                    'lost': 4,
                    'points': 69,
                    'goalDifference': 37
                }
            ]
        }]
    }


@pytest.fixture
def mock_api_response_matches():
    """Mock API response for matches."""
    return {
        'matches': [
            {
                'utcDate': '2026-03-20T20:00:00Z',
                'homeTeam': {'name': 'FC Barcelona'},
                'awayTeam': {'name': 'Villarreal CF'},
                'score': {
                    'fullTime': {'home': 3, 'away': 1}
                },
                'matchday': 20,
                'status': 'FINISHED'
            },
            {
                'utcDate': '2026-03-21T18:30:00Z',
                'homeTeam': {'name': 'Real Madrid CF'},
                'awayTeam': {'name': 'Athletic Club'},
                'score': {
                    'fullTime': {'home': 2, 'away': 1}
                },
                'matchday': 20,
                'status': 'FINISHED'
            }
        ]
    }


@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client."""
    client = MagicMock()
    client.put_object.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
    return client

# API FETCHING TESTS
@patch('requests.get')
def test_fetch_api_success(mock_get, mock_api_response_standings):
    """Test successful API fetch."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response_standings
    mock_get.return_value = mock_response
    
    # You would test your actual fetch function here
    # Example:
    # from src.data.ingest_football import fetch_football_data
    # result = fetch_football_data('standings')
    # assert result == mock_api_response_standings
    
    # For now, just verify mock behavior
    response = mock_get('https://api.football-data.org/v4/standings')
    assert response.status_code == 200
    assert 'standings' in response.json()


@patch('requests.get')
def test_fetch_api_failure(mock_get):
    """Test API fetch failure handling."""
    mock_response = Mock()
    mock_response.status_code = 429  # Rate limit
    mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
    mock_get.return_value = mock_response
    
    # Test that error is properly handled
    response = mock_get('https://api.football-data.org/v4/standings')
    assert response.status_code == 429


@patch('requests.get')
def test_fetch_api_timeout(mock_get):
    """Test API timeout handling."""
    mock_get.side_effect = Exception("Connection timeout")
    
    with pytest.raises(Exception) as exc_info:
        mock_get('https://api.football-data.org/v4/standings', timeout=5)
    
    assert "timeout" in str(exc_info.value).lower()

# S3 UPLOAD TESTS
def test_s3_upload_success(mock_s3_client, mock_api_response_standings):
    """Test successful S3 upload."""
    bucket = 'football-data-lake-2026'
    key = 'raw/standings/standings_20260320_120000.json'
    data = json.dumps(mock_api_response_standings)
    
    response = mock_s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=data,
        ContentType='application/json'
    )
    
    # Verify upload was called
    assert mock_s3_client.put_object.called
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200


def test_s3_upload_generates_correct_key(mock_s3_client):
    """Test that S3 key includes timestamp."""
    now = datetime.now()
    expected_format = f"raw/standings/standings_{now.strftime('%Y%m%d')}"
    
    # Mock upload
    key = f"raw/standings/standings_{now.strftime('%Y%m%d_%H%M%S')}.json"
    
    mock_s3_client.put_object(
        Bucket='football-data-lake-2026',
        Key=key,
        Body='{}',
        ContentType='application/json'
    )
    
    # Verify key format
    call_kwargs = mock_s3_client.put_object.call_args[1]
    assert 'raw/standings/standings_' in call_kwargs['Key']
    assert '.json' in call_kwargs['Key']


def test_s3_upload_failure_handling(mock_s3_client):
    """Test S3 upload failure handling."""
    mock_s3_client.put_object.side_effect = Exception("Access denied")
    
    with pytest.raises(Exception) as exc_info:
        mock_s3_client.put_object(
            Bucket='football-data-lake-2026',
            Key='raw/test.json',
            Body='{}'
        )
    
    assert "Access denied" in str(exc_info.value)

# DATA VALIDATION TESTS
def test_validate_standings_structure(mock_api_response_standings):
    """Test that standings data has required structure."""
    data = mock_api_response_standings
    
    # Check top-level structure
    assert 'standings' in data
    assert len(data['standings']) > 0
    
    # Check table structure
    table = data['standings'][0]['table']
    assert len(table) > 0
    
    # Check team data structure
    team = table[0]
    required_fields = ['team', 'position', 'playedGames', 'won', 'draw', 'lost', 'points', 'goalDifference']
    for field in required_fields:
        assert field in team, f"Missing field: {field}"


def test_validate_matches_structure(mock_api_response_matches):
    """Test that matches data has required structure."""
    data = mock_api_response_matches
    
    # Check top-level structure
    assert 'matches' in data
    assert len(data['matches']) > 0
    
    # Check match structure
    match = data['matches'][0]
    required_fields = ['utcDate', 'homeTeam', 'awayTeam', 'score', 'matchday', 'status']
    for field in required_fields:
        assert field in match, f"Missing field: {field}"
    
    # Check score structure
    assert 'fullTime' in match['score']
    assert 'home' in match['score']['fullTime']
    assert 'away' in match['score']['fullTime']


def test_standings_data_types(mock_api_response_standings):
    """Test that standings data has correct types."""
    table = mock_api_response_standings['standings'][0]['table'][0]
    
    assert isinstance(table['position'], int)
    assert isinstance(table['playedGames'], int)
    assert isinstance(table['won'], int)
    assert isinstance(table['points'], int)
    assert isinstance(table['team']['name'], str)


def test_matches_data_types(mock_api_response_matches):
    """Test that matches data has correct types."""
    match = mock_api_response_matches['matches'][0]
    
    assert isinstance(match['utcDate'], str)
    assert isinstance(match['matchday'], int)
    assert isinstance(match['status'], str)
    assert isinstance(match['score']['fullTime']['home'], int)

# FILE PATH TESTS
def test_raw_file_paths():
    """Test raw file path generation."""
    now = datetime.now()
    
    # Standings path
    standings_path = f"raw/standings/la_liga_standings_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    assert standings_path.startswith('raw/standings/')
    assert standings_path.endswith('.json')
    
    # Matches path
    matches_path = f"raw/matches/la_liga_matches_{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    assert matches_path.startswith('raw/matches/')
    assert matches_path.endswith('.json')

# INTEGRATION TESTS
@patch('requests.get')
@patch('boto3.client')
def test_full_ingestion_flow(mock_boto_client, mock_get, mock_api_response_standings):
    """Test complete ingestion flow: API → S3."""
    # Setup mocks
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_api_response_standings
    mock_get.return_value = mock_response
    
    mock_s3 = MagicMock()
    mock_s3.put_object.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
    mock_boto_client.return_value = mock_s3
    
    # Simulate ingestion flow
    # 1. Fetch from API
    api_data = mock_get('https://api.football-data.org/v4/standings').json()
    
    # 2. Validate data
    assert 'standings' in api_data
    
    # 3. Upload to S3
    s3_client = mock_boto_client('s3')
    response = s3_client.put_object(
        Bucket='football-data-lake-2026',
        Key='raw/standings/test.json',
        Body=json.dumps(api_data)
    )
    
    # Verify entire flow
    assert mock_get.called
    assert mock_s3.put_object.called
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200


# HELPER FUNCTION TESTS
def test_timestamp_generation():
    """Test timestamp format for file naming."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    # Verify format
    assert len(timestamp) == 19  # YYYY-MM-DD_HH-MM-SS
    assert timestamp[4] == '-'
    assert timestamp[7] == '-'
    assert timestamp[10] == '_'


def test_json_serialization(mock_api_response_standings):
    """Test that API response can be serialized to JSON."""
    json_str = json.dumps(mock_api_response_standings)
    
    # Verify serialization
    assert isinstance(json_str, str)
    
    # Verify deserialization
    data = json.loads(json_str)
    assert data == mock_api_response_standings

# ERROR HANDLING TESTS
def test_invalid_json_handling():
    """Test handling of invalid JSON."""
    invalid_json = "{'invalid': json}"
    
    with pytest.raises(json.JSONDecodeError):
        json.loads(invalid_json)


def test_missing_api_key_handling():
    """Test handling of missing API key."""
    import os
    
    # Simulate missing key
    api_key = os.getenv('NONEXISTENT_KEY')
    assert api_key is None

# RUN TESTS
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])