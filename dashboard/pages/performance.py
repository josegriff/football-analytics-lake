"""
Team Performance page - charts and analytics.
"""

import streamlit as st
from src.utils.athena_clients import load_standings
from dashboard.components.charts import (
    create_points_chart,
    create_goal_difference_scatter,
    create_form_heatmap
)


def render():
    """Render the Team Performance page."""
    st.title("Team Performance")
    
    try:
        with st.spinner("Loading data..."):
            df = load_standings()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            top = df.iloc[0]
            st.metric("Leader", top['team'], f"{top['points']} pts")
        
        with col2:
            best_gd = df.loc[df['goalDifference'].idxmax()]
            st.metric("Best GD", best_gd['team'], f"+{best_gd['goalDifference']}")
        
        with col3:
            most_wins = df.loc[df['won'].idxmax()]
            st.metric("Most Wins", most_wins['team'], f"{most_wins['won']}")
        
        with col4:
            st.metric("Avg Points", f"{df['points'].mean():.1f}", "per team")
        
        # Charts in tabs
        tab1, tab2, tab3 = st.tabs(["Points", "Matrix", "Form"])
        
        with tab1:
            st.plotly_chart(create_points_chart(df), use_container_width=True)
        
        with tab2:
            st.plotly_chart(create_goal_difference_scatter(df), use_container_width=True)
        
        with tab3:
            st.plotly_chart(create_form_heatmap(df), use_container_width=True)
    
    except Exception as e:
        st.error(f"Error: {e}")