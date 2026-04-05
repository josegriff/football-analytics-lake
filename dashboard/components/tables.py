"""
Table components for standings and match results.
"""

from dashboard.config import TEAM_BADGES, COMPETITION_ZONES
from dashboard.components.navigation import get_theme_colors


def get_team_badge_html(team_name):
    """Generate HTML for team badge + name."""
    badge_url = TEAM_BADGES.get(team_name, '')
    if badge_url:
        return f'<img src="{badge_url}" class="team-badge" onerror="this.style.display=\'none\'">{team_name}'
    return team_name


def get_zone_badge(position):
    """Generate zone badge HTML based on position."""
    for zone_key, zone_data in COMPETITION_ZONES.items():
        if position in zone_data['positions']:
            return f'<span class="zone-badge {zone_key}-badge">{zone_data["badge"]}</span>'
    return ''


def create_standings_table_html(df):
    """
    Create styled HTML standings table.
    
    Args:
        df (pd.DataFrame): Standings data
        
    Returns:
        str: HTML table
    """
    colors = get_theme_colors()
    
    html = f"""
    <table style="width:100%; border-collapse: collapse; font-family: 'Segoe UI', sans-serif;">
        <thead>
            <tr style="background-color: {colors['bg_secondary']}; border-bottom: 2px solid {colors['border']};">
                <th style="padding: 12px; text-align: left;">Pos</th>
                <th style="padding: 12px; text-align: left;">Team</th>
                <th style="padding: 12px; text-align: center;">Played</th>
                <th style="padding: 12px; text-align: center;">W</th>
                <th style="padding: 12px; text-align: center;">D</th>
                <th style="padding: 12px; text-align: center;">L</th>
                <th style="padding: 12px; text-align: center;">GD</th>
                <th style="padding: 12px; text-align: center; background-color: {colors['points_col']}33; font-weight: bold;">Pts</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for _, row in df.iterrows():
        row_bg = colors['bg_secondary'] if row['position'] % 2 == 0 else colors['bg_primary']
        
        html += f"""
        <tr style="background-color: {row_bg}; border-bottom: 1px solid {colors['border']};">
            <td style="padding: 12px; font-weight: bold;">{row['position']}</td>
            <td style="padding: 12px;">
                {get_team_badge_html(row['team'])}
                {get_zone_badge(row['position'])}
            </td>
            <td style="padding: 12px; text-align: center;">{row['playedGames']}</td>
            <td style="padding: 12px; text-align: center; color: {colors['success']};">{row['won']}</td>
            <td style="padding: 12px; text-align: center; color: {colors['warning']};">{row['draw']}</td>
            <td style="padding: 12px; text-align: center; color: {colors['accent']};">{row['lost']}</td>
            <td style="padding: 12px; text-align: center; font-weight: 500;">{row['goalDifference']:+d}</td>
            <td style="padding: 12px; text-align: center; background-color: {colors['points_col']}33; font-weight: bold; font-size: 1.1em;">{row['points']}</td>
        </tr>
        """
    
    html += "</tbody></table>"
    return html