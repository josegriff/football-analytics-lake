"""
Navigation bar component with theme toggle and page selection.
"""

import streamlit as st
from dashboard.config import DARK_THEME, LIGHT_THEME


def initialize_theme():
    """Initialize theme in session state."""
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'


def toggle_theme():
    """Toggle between light and dark theme."""
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'


def get_theme_colors():
    """
    Get current theme colors.
    
    Returns:
        dict: Color scheme
    """
    return DARK_THEME if st.session_state.theme == 'dark' else LIGHT_THEME


def apply_custom_css():
    """Apply theme-based custom CSS."""
    colors = get_theme_colors()
    
    css = f"""
    <style>
    .main {{background-color: {colors['bg_primary']};}}
    .metric-card {{
        background-color: {colors['bg_secondary']};
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid {colors['border']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }}
    .metric-card:hover {{transform: translateY(-2px);}}
    .team-badge {{width: 24px; height: 24px; margin-right: 8px; vertical-align: middle;}}
    .zone-badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-left: 8px;
    }}
    .ucl-badge {{background-color: #0066CC; color: white;}}
    .europa-badge {{background-color: #FF6600; color: white;}}
    .relegation-badge {{background-color: #CC0000; color: white;}}
    h1, h2, h3 {{color: {colors['text_primary']};}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_navigation():
    """
    Render horizontal navigation bar.
    
    Returns:
        str: Selected page name
    """
    # Initialize session state if not exists
    initialize_theme()
    
    col1, col2, col3 = st.columns([2, 3, 1])
    
    with col1:
        st.markdown("### La Liga Analytics")
    
    with col2:
        page = st.selectbox(
            "Navigate to",
            ["League Table", "Team Performance", "Match Results", "Statistics"],
            label_visibility="collapsed"
        )
    
    with col3:
        theme_icon = "🌙" if st.session_state.theme == 'light' else "☀️"
        if st.button(f"{theme_icon} Theme", use_container_width=True):
            toggle_theme()
            st.rerun()
    

    st.markdown("---")
    
    return page