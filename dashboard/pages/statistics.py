"""
Statistics page - league-wide analytics.
"""

import streamlit as st
from src.utils.athena_clients import get_home_away_stats, load_matches
from dashboard.components.charts import create_home_away_pie


def render():
    """Render the Statistics page."""
    st.title("League Statistics")
    
    try:
        with st.spinner("Calculating stats..."):
            matches_df = load_matches()
            home_away_df = get_home_away_stats()
        
        # Key metrics
        total_matches = len(matches_df)
        total_goals = (matches_df['homeScore'] + matches_df['awayScore']).sum()
        avg_goals = total_goals / total_matches
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Matches", total_matches)
        
        with col2:
            st.metric("Goals", int(total_goals))
        
        with col3:
            st.metric("Goals/Match", f"{avg_goals:.2f}")
        
        with col4:
            home_wins = home_away_df[home_away_df['result'] == 'Home Win']['percentage'].values
            if len(home_wins) > 0:
                st.metric("Home Win %", f"{home_wins[0]:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_home_away_pie(home_away_df), use_container_width=True)
        
        with col2:
            st.markdown("###Breakdown")
            for _, row in home_away_df.iterrows():
                st.metric(row['result'], f"{row['match_count']} matches", f"{row['percentage']}%")
    
    except Exception as e:
        st.error(f"Error: {e}")