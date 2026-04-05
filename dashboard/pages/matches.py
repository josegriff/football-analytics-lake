"""
Match Results page - recent fixtures and results.
"""

import streamlit as st
from src.utils.athena_clients import load_matches


def render():
    """Render the Match Results page."""
    st.title("Recent Matches")
    
    try:
        with st.spinner("Loading matches..."):
            df = load_matches()
        
        # Filters
        col1, col2 = st.columns([3, 1])
        
        with col1:
            teams = sorted(set(df['homeTeam']) | set(df['awayTeam']))
            team = st.selectbox("Filter by team", ["All Teams"] + teams)
        
        with col2:
            limit = st.number_input("Show", 5, 50, 20, 5)
        
        # Apply filters
        if team != "All Teams":
            df = df[(df['homeTeam'] == team) | (df['awayTeam'] == team)]
        df = df.head(limit)
        
        st.info(f"{len(df)} matches", icon="ℹ️")
        
        # Display matches
        for _, match in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
            
            home_won = match['homeScore'] > match['awayScore']
            away_won = match['awayScore'] > match['homeScore']
            
            with col1:
                st.markdown(f"**{match['homeTeam']}**" if home_won else match['homeTeam'])
            
            with col2:
                st.markdown(f"<div style='text-align:center; font-size:1.5em; font-weight:bold;'>{match['homeScore']}</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown("<div style='text-align:center;'>-</div>", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"<div style='text-align:center; font-size:1.5em; font-weight:bold;'>{match['awayScore']}</div>", unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"**{match['awayTeam']}**" if away_won else match['awayTeam'])
            
            st.caption(f"{match['utcDate'].strftime('%b %d, %Y %H:%M')} | MD {match['matchday']}")
            st.markdown("---")
    
    except Exception as e:
        st.error(f"Error: {e}")