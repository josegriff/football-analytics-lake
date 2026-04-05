"""
League Table page - displays current league standings with football format.
"""

import streamlit as st
from src.utils.athena_clients import load_standings
from dashboard.config import TEAM_BADGES, COMPETITION_ZONES


def get_competition_zone(position):
    """Get competition zone info for a given position."""
    for zone_key, zone_data in COMPETITION_ZONES.items():
        if position in zone_data['positions']:
            return zone_data
    return None


def get_team_badge(team_name):
    """Get team badge URL or return text fallback."""
    badge_url = TEAM_BADGES.get(team_name, '')
    if badge_url:
        return f'<img src="{badge_url}" width="24" height="24" style="vertical-align: middle; margin-right: 8px;" onerror="this.style.display=\'none\'">'
    return ''


def create_football_dataframe(df):
    """Create a football-formatted dataframe for the league table."""
    df_display = df.copy()
    
    # Format team names without HTML badges (just text)
    df_display['Team'] = df_display['team']
    
    # Calculate goals for and against (assuming we have these columns or need to derive them)
    # For now, we'll use placeholder values - you may need to adjust based on your actual data
    if 'goalsFor' not in df_display.columns:
        df_display['goalsFor'] = df_display['goalDifference'] + df_display.get('goalsAgainst', 0)
    if 'goalsAgainst' not in df_display.columns:
        df_display['goalsAgainst'] = df_display['goalsFor'] - df_display['goalDifference']
    
    # Format goal difference
    df_display['GD'] = df_display['goalDifference'].apply(lambda gd: f"+{gd}" if gd > 0 else str(gd))
    
    # Select and reorder columns in football format (removed Zone)
    columns = ['position', 'Team', 'playedGames', 'won', 'draw', 'lost', 'goalsFor', 'goalsAgainst', 'GD', 'points']
    df_display = df_display[columns]
    
    # Rename columns for display
    df_display.columns = ['Pos', 'Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'PTS']
    
    return df_display


def apply_zone_styling(df):
    """Apply conditional styling based on competition zones."""
    def highlight_zone(row):
        zone = get_competition_zone(row['Pos'])
        if zone:
            return [f'background-color: {zone["color"]}20; color: {zone["color"]}; font-weight: bold'] + [''] * 9
        return [''] * 10
    
    return df.style.apply(highlight_zone, axis=1)


def render():
    """Render the League Table page."""
    st.title("League Table")
    st.markdown("Current La Liga standings")
    
    try:
        with st.spinner("Loading latest standings..."):
            df = load_standings()
            df = df.rename(columns={
                'goalsfor': 'goalsScored',
                'goalsagainst': 'goalsConceded',
                'goaldifference': 'goalDifference',
                'playedgames': 'playedGames'
            })
        
            # Handle potential partition columns if not present (fallback)
            if 'year' not in df.columns:
                df['year'] = 2026
            if 'month' not in df.columns:
                df['month'] = 1
            if 'week' not in df.columns:
                df['week'] = 1
        
        if df.empty:
            st.warning("No data available. Please check your data source.")
            return
        
        # Key metrics at the top
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            leader = df.iloc[0]
            st.metric("Leader", leader['team'], f"{leader['points']} pts")
        
        with col2:
            best_gd = df.loc[df['goalDifference'].idxmax()]
            st.metric("Best GD", best_gd['team'], f"+{best_gd['goalDifference']}")
        
        with col3:
            most_wins = df.loc[df['won'].idxmax()]
            st.metric("Most Wins", most_wins['team'], f"{most_wins['won']}")
        
        with col4:
            avg_points = df['points'].mean()
            st.metric("Avg Points", f"{avg_points:.1f}", "per team")
        
        st.markdown("---")
        
        # Create football-formatted dataframe
        df_football = create_football_dataframe(df)
        
        # Display the table with styling
        styled_df = apply_zone_styling(df_football)
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Team badges display
        st.markdown("### Team Badges")
        teams = df['team'].unique()
        cols = st.columns(4)
        
        for i, team in enumerate(teams):
            with cols[i % 4]:
                badge_url = TEAM_BADGES.get(team, '')
                if badge_url:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px;">
                        <img src="{badge_url}" width="40" height="40" style="margin-bottom: 5px;" onerror="this.style.display='none'">
                        <div style="font-size: 0.9em;">{team}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px;">
                        <div style="width: 40px; height: 40px; background-color: #f0f0f0; margin: 0 auto 5px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                            {team[:3].upper()}
                        </div>
                        <div style="font-size: 0.9em;">{team}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Competition zones legend with colored dots
        st.markdown("### Competition Qualification")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ucl_zone = COMPETITION_ZONES['ucl']
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="width: 20px; height: 20px; background-color: {ucl_zone['color']}; border-radius: 50%; margin: 0 auto 5px;"></div>
                <strong>{ucl_zone['name']}</strong><br>
                <small>Positions {min(ucl_zone['positions'])}-{max(ucl_zone['positions'])}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            europa_zone = COMPETITION_ZONES['europa']
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="width: 20px; height: 20px; background-color: {europa_zone['color']}; border-radius: 50%; margin: 0 auto 5px;"></div>
                <strong>{europa_zone['name']}</strong><br>
                <small>Position {europa_zone['positions'].start}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            uecl_zone = COMPETITION_ZONES['uecl']
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="width: 20px; height: 20px; background-color: {uecl_zone['color']}; border-radius: 50%; margin: 0 auto 5px;"></div>
                <strong>{uecl_zone['name']}</strong><br>
                <small>Position {uecl_zone['positions'].start}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            relegation_zone = COMPETITION_ZONES['relegation']
            st.markdown(f"""
            <div style="text-align: center; padding: 10px;">
                <div style="width: 20px; height: 20px; background-color: {relegation_zone['color']}; border-radius: 50%; margin: 0 auto 5px;"></div>
                <strong>{relegation_zone['name']}</strong><br>
                <small>Positions {min(relegation_zone['positions'])}-{max(relegation_zone['positions'])}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional statistics
        st.markdown("---")
        st.markdown("### Season Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Use actual goals data from transformed data
            total_goals_for = df['goalsScored'].sum()
            st.metric("Goals For", int(total_goals_for))
        
        with col2:
            total_goals_against = df['goalsConceded'].sum()
            st.metric("Goals Against", int(total_goals_against))
        
        with col3:
            total_matches = df['playedGames'].sum()
            st.metric("Total Matches", total_matches)
        
        with col4:
            avg_goals_per_match = (df['goalsScored'].sum() + df['goalsConceded'].sum()) / (df['playedGames'].sum() / 2) if df['playedGames'].sum() > 0 else 0
            st.metric("Goals/Match", f"{avg_goals_per_match:.2f}")
        
    except Exception as e:
        st.error(f"Error loading league table: {e}")
        st.info("Please check your AWS Athena connection and S3 bucket configuration.")

