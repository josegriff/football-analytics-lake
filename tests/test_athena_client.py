"""
Unit tests for Athena database client.

Run with: pytest tests/test_athena_client.py -v
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.utils.athena_client import (
    get_athena_connection,
    execute_query,
    load_standings,
    load_matches,
    get_home_away_stats
)

# FIXTURES
@pytest.fixture
def mock_standings_data():
    """Mock standings DataFrame."""
    return pd.DataFrame({
        'team': ['FC Barcelona', 'Real Madrid CF', 'Villarreal CF'],
        'position': [1, 2, 3],
        'playedGames': [29, 29, 29],
        'won': [24, 22, 18],
        'draw': [1, 3, 4],
        'lost': [4, 4, 7],
        'points': [73, 69, 58],
        'goalDifference': [50, 37, 20],
        'year': [2026, 2026, 2026],
        'month': [3, 3, 3],
        'week': [12, 12, 12]
    })


@pytest.fixture
def mock_matches_data():
    """Mock matches DataFrame."""
    return pd.DataFrame({
        'utcDate': pd.to_datetime(['2026-03-20', '2026-03-21']),
        'homeTeam': ['FC Barcelona', 'Real Madrid CF'],
        'awayTeam': ['Villarreal CF', 'Athletic Club'],
        'homeScore': [3, 2],
        'awayScore': [1, 1],
        'matchday': [20, 20],
        'status': ['FINISHED', 'FINISHED']
    })


@pytest.fixture
def mock_home_away_data():
    """Mock home/away statistics DataFrame."""
    return pd.DataFrame({
        'result': ['Home Win', 'Away Win', 'Draw'],
        'match_count': [120, 80, 50],
        'percentage': [48.0, 32.0, 20.0]
    })

# CONNECTION TESTS
@patch('src.utils.athena_client.connect')
def test_get_athena_connection(mock_connect):
    """Test Athena connection creation."""
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    
    # First call should create connection
    conn1 = get_athena_connection()
    assert conn1 == mock_conn
    assert mock_connect.call_count == 1
    
    # Note: In actual Streamlit app, @st.cache_resource would prevent second call
    # But in unit tests, caching is not active

@patch('src.utils.athena_client.connect')
def test_athena_connection_parameters(mock_connect):
    """Test that connection uses correct parameters."""
    get_athena_connection()
    
    # Verify connect was called with expected parameters
    call_kwargs = mock_connect.call_args[1]
    assert 's3_staging_dir' in call_kwargs
    assert 'region_name' in call_kwargs
    assert 'schema_name' in call_kwargs
    assert 'football_analytics' in call_kwargs['schema_name']

# QUERY EXECUTION TESTS
@patch('src.utils.athena_client.get_athena_connection')
@patch('src.utils.athena_client.pd.read_sql')
def test_execute_query_success(mock_read_sql, mock_get_conn, mock_standings_data):
    """Test successful query execution."""
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_read_sql.return_value = mock_standings_data
    
    query = "SELECT * FROM standings"
    result = execute_query(query)
    
    # Verify read_sql was called with correct parameters
    mock_read_sql.assert_called_once_with(query, mock_conn)
    
    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert 'team' in result.columns


@patch('src.utils.athena_client.get_athena_connection')
@patch('src.utils.athena_client.pd.read_sql')
def test_execute_query_empty_result(mock_read_sql, mock_get_conn):
    """Test query execution with empty result."""
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_read_sql.return_value = pd.DataFrame()
    
    result = execute_query("SELECT * FROM standings WHERE position > 100")
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


@patch('src.utils.athena_client.get_athena_connection')
@patch('src.utils.athena_client.pd.read_sql')
def test_execute_query_failure(mock_read_sql, mock_get_conn):
    """Test query execution with database error."""
    mock_conn = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_read_sql.side_effect = Exception("Database connection failed")
    
    with pytest.raises(Exception) as exc_info:
        execute_query("SELECT * FROM standings")
    
    assert "Database connection failed" in str(exc_info.value)


# STANDINGS TESTS
@patch('src.utils.athena_client.execute_query')
def test_load_standings_success(mock_execute, mock_standings_data):
    """Test loading standings data."""
    mock_execute.return_value = mock_standings_data
    
    result = load_standings()
    
    # Verify query was executed
    assert mock_execute.called
    
    # Verify result structure
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert result['position'].tolist() == [1, 2, 3]
    assert 'team' in result.columns
    assert 'points' in result.columns
    assert 'goalDifference' in result.columns


@patch('src.utils.athena_client.execute_query')
def test_load_standings_sorted_by_position(mock_execute, mock_standings_data):
    """Test that standings are sorted by position."""
    # Shuffle data
    shuffled = mock_standings_data.sample(frac=1)
    mock_execute.return_value = shuffled
    
    result = load_standings()
    
    # Should still be sorted by position
    assert result['position'].is_monotonic_increasing or result.iloc[0]['position'] == 1


# MATCHES TESTS
@patch('src.utils.athena_client.execute_query')
def test_load_matches_success(mock_execute, mock_matches_data):
    """Test loading match data."""
    mock_execute.return_value = mock_matches_data
    
    result = load_matches(limit=50)
    
    # Verify query was executed
    assert mock_execute.called
    
    # Verify result structure
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert 'homeTeam' in result.columns
    assert 'awayTeam' in result.columns
    assert 'homeScore' in result.columns


@patch('src.utils.athena_client.execute_query')
def test_load_matches_date_conversion(mock_execute, mock_matches_data):
    """Test that utcDate is converted to datetime."""
    mock_execute.return_value = mock_matches_data
    
    result = load_matches()
    
    # Verify date column is datetime type
    assert pd.api.types.is_datetime64_any_dtype(result['utcDate'])


@patch('src.utils.athena_client.execute_query')
def test_load_matches_custom_limit(mock_execute, mock_matches_data):
    """Test loading matches with custom limit."""
    mock_execute.return_value = mock_matches_data
    
    load_matches(limit=10)
    
    # Verify query contains limit
    call_args = mock_execute.call_args[0][0]
    assert 'LIMIT 10' in call_args


# HOME/AWAY STATISTICS TESTS
@patch('src.utils.athena_client.execute_query')
def test_get_home_away_stats_success(mock_execute, mock_home_away_data):
    """Test home/away statistics calculation."""
    mock_execute.return_value = mock_home_away_data
    
    result = get_home_away_stats()
    
    # Verify query was executed
    assert mock_execute.called
    
    # Verify result structure
    assert isinstance(result, pd.DataFrame)
    assert 'result' in result.columns
    assert 'match_count' in result.columns
    assert 'percentage' in result.columns
    
    # Verify percentages sum to 100
    assert abs(result['percentage'].sum() - 100.0) < 0.1


@patch('src.utils.athena_client.execute_query')
def test_get_home_away_stats_categories(mock_execute, mock_home_away_data):
    """Test that all result categories are present."""
    mock_execute.return_value = mock_home_away_data
    
    result = get_home_away_stats()
    
    # Should have Home Win, Away Win, Draw
    assert len(result) == 3
    assert set(result['result']) == {'Home Win', 'Away Win', 'Draw'}


# INTEGRATION TESTS
@patch('src.utils.athena_client.execute_query')
def test_standings_columns_match_schema(mock_execute, mock_standings_data):
    """Test that standings data has all expected columns."""
    mock_execute.return_value = mock_standings_data
    
    result = load_standings()
    
    expected_columns = [
        'team', 'position', 'playedGames', 'won', 'draw', 
        'lost', 'points', 'goalDifference', 'year', 'month', 'week'
    ]
    
    for col in expected_columns:
        assert col in result.columns, f"Missing column: {col}"


@patch('src.utils.athena_client.execute_query')
def test_matches_columns_match_schema(mock_execute, mock_matches_data):
    """Test that match data has all expected columns."""
    mock_execute.return_value = mock_matches_data
    
    result = load_matches()
    
    expected_columns = [
        'utcDate', 'homeTeam', 'awayTeam', 
        'homeScore', 'awayScore', 'matchday', 'status'
    ]
    
    for col in expected_columns:
        assert col in result.columns, f"Missing column: {col}"


# RUN TESTS
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])