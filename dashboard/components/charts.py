"""
Chart components using Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
from dashboard.components.navigation import get_theme_colors


def create_points_chart(df):
    """Create horizontal bar chart of points."""
    colors = get_theme_colors()
    df_sorted = df.sort_values('points', ascending=True)
    
    fig = px.bar(
        df_sorted,
        x='points',
        y='team',
        orientation='h',
        title='Points Distribution',
        color='points',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        height=700,
        showlegend=False,
        paper_bgcolor=colors['bg_primary'],
        plot_bgcolor=colors['bg_secondary'],
        font=dict(color=colors['text_primary'])
    )
    
    return fig


def create_goal_difference_scatter(df):
    """Create scatter plot of points vs goal difference."""
    colors = get_theme_colors()
    
    fig = px.scatter(
        df,
        x='goalDifference',
        y='points',
        text='team',
        title='Performance Matrix: Points vs Goal Difference',
        color='position',
        color_continuous_scale='RdYlGn_r',
        size='playedGames',
        hover_data=['won', 'draw', 'lost']
    )
    
    fig.update_traces(textposition='top center', textfont_size=9)
    fig.update_layout(
        height=600,
        paper_bgcolor=colors['bg_primary'],
        plot_bgcolor=colors['bg_secondary'],
        font=dict(color=colors['text_primary'])
    )
    
    return fig


def create_home_away_pie(df):
    """Create pie chart of match outcomes."""
    colors = get_theme_colors()
    
    fig = px.pie(
        df,
        values='match_count',
        names='result',
        title='Match Outcome Distribution',
        color='result',
        color_discrete_map={
            'Home Win': '#00D084',
            'Away Win': '#FF4B4B',
            'Draw': '#FFA500'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        paper_bgcolor=colors['bg_primary'],
        font=dict(color=colors['text_primary'])
    )
    
    return fig


def create_form_heatmap(df):
    """Create heatmap of team form (W/D/L)."""
    colors = get_theme_colors()
    form_data = df[['team', 'won', 'draw', 'lost']].set_index('team')
    
    fig = go.Figure(data=go.Heatmap(
        z=form_data.values.T,
        x=form_data.index,
        y=['Wins', 'Draws', 'Losses'],
        colorscale='RdYlGn',
        text=form_data.values.T,
        texttemplate='%{text}'
    ))
    
    fig.update_layout(
        title='Team Form Heatmap',
        height=300,
        paper_bgcolor=colors['bg_primary'],
        plot_bgcolor=colors['bg_secondary'],
        font=dict(color=colors['text_primary']),
        xaxis={'tickangle': 45}
    )
    
    return fig