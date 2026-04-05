"""
Football Analytics Dashboard - Main Entry Point

Modular Streamlit app with component-based architecture.
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
from dashboard.config import APP_CONFIG
from dashboard.components.navigation import (
    initialize_theme,
    apply_custom_css,
    render_navigation
)
from dashboard.pages import (
    league_table,
    performance,
    matches,
    statistics
)


# MAIN APP
def main():
    """Main application entry point."""
    
    # Configure page
    st.set_page_config(
        page_title=APP_CONFIG['page_title'],
        page_icon=APP_CONFIG['page_icon'],
        layout=APP_CONFIG['layout'],
        initial_sidebar_state="collapsed"
    )
    
    # Initialize theme
    initialize_theme()
    apply_custom_css()
    
    # Render navigation
    page = render_navigation()
    
    # Refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Route to appropriate page
    page_map = {
        "League Table": league_table,
        "Team Performance": performance,
        "Match Results": matches,
        "Statistics": statistics
    }
    
    page_map[page].render()
    
    # Footer
    st.markdown("---")
    st.caption("S3 Data Lake → Athena → Streamlit | Cached 1hr")


if __name__ == "__main__":
    main()