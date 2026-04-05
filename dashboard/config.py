"""
Dashboard configuration - themes, colors, and constants.
"""

# THEME COLORS
DARK_THEME = {
    'bg_primary': '#0E1117',
    'bg_secondary': '#262730',
    'text_primary': '#FAFAFA',
    'text_secondary': '#A0A0A0',
    'accent': '#FF4B4B',
    'success': '#00D084',
    'warning': '#FFA500',
    'info': '#00A8E8',
    'points_col': '#FFD700',
    'border': '#404040'
}

LIGHT_THEME = {
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F0F2F6',
    'text_primary': '#0E1117',
    'text_secondary': '#666666',
    'accent': '#FF4B4B',
    'success': '#00C853',
    'warning': '#FF6F00',
    'info': '#0288D1',
    'points_col': '#FFA726',
    'border': '#E0E0E0'
}

# TEAM BADGES
TEAM_BADGES = {
    'FC Barcelona': 'https://upload.wikimedia.org/wikipedia/en/4/47/FC_Barcelona_%28crest%29.svg',
    'Real Madrid CF': 'https://upload.wikimedia.org/wikipedia/en/5/56/Real_Madrid_CF.svg',
    'Atlético Madrid': 'https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg',
    'Club Atlético de Madrid': 'https://upload.wikimedia.org/wikipedia/en/f/f4/Atletico_Madrid_2017_logo.svg',
    'Villarreal CF': 'https://upload.wikimedia.org/wikipedia/en/b/b9/Villarreal_CF_logo-en.svg',
    'Real Betis Balompié': 'https://upload.wikimedia.org/wikipedia/en/1/13/Real_betis_logo.svg',
    'Athletic Club': 'https://upload.wikimedia.org/wikipedia/en/9/98/Club_Athletic_Bilbao_logo.svg',
    'Real Sociedad de Fútbol': 'https://upload.wikimedia.org/wikipedia/en/f/f1/Real_Sociedad_logo.svg',
    'Valencia CF': 'https://upload.wikimedia.org/wikipedia/en/c/ce/Valenciacf.svg',
    'Sevilla FC': 'https://upload.wikimedia.org/wikipedia/en/3/3b/Sevilla_FC_logo.svg',
    'Getafe CF': 'https://upload.wikimedia.org/wikipedia/en/4/46/Getafe_logo.svg',
    'CA Osasuna': 'https://upload.wikimedia.org/wikipedia/en/1/1f/CA_Osasuna_logo.svg',
    'RC Celta de Vigo': 'https://upload.wikimedia.org/wikipedia/en/1/12/RC_Celta_de_Vigo_logo.svg',
    'Rayo Vallecano de Madrid': 'https://upload.wikimedia.org/wikipedia/en/c/ce/Rayo_Vallecano_logo.svg',
    'RCD Mallorca': 'https://upload.wikimedia.org/wikipedia/en/e/e0/RCD_Mallorca.svg',
    'Girona FC': 'https://upload.wikimedia.org/wikipedia/en/7/79/Girona_FC_logo.svg',
    'RCD Espanyol de Barcelona': 'https://upload.wikimedia.org/wikipedia/en/8/82/RCD_Espanyol_logo.svg',
    'Deportivo Alavés': 'https://upload.wikimedia.org/wikipedia/en/c/c2/Deportivo_Alaves_logo.svg',
    'Elche CF': 'https://upload.wikimedia.org/wikipedia/en/2/20/Elche_CF_logo.svg',
    'Levante UD': 'https://upload.wikimedia.org/wikipedia/en/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg',
    'Real Oviedo': 'https://upload.wikimedia.org/wikipedia/en/6/6b/Real_Oviedo_logo.svg'
}

# APP SETTINGS
APP_CONFIG = {
    'page_title': '⚽ La Liga Analytics',
    'page_icon': '⚽',
    'layout': 'wide',
    'cache_ttl': 3600,  # 1 hour in seconds
    's3_bucket': 'football-data-lake-2026',
    'aws_region': 'eu-north-1',
    'athena_database': 'football_analytics'
}

# COMPETITION ZONES
COMPETITION_ZONES = {
    'ucl': {
        'name': 'Champions League',
        'positions': range(1, 5),
        'color': '#0066CC',
        'badge': 'UCL',
        'emoji': '🏆'
    },
    'europa': {
        'name': 'Europa League',
        'positions': range(5, 6),
        'color': '#FF6600',
        'badge': 'UEL',
        'emoji': '⚽'
    },
    'uecl': {
        'name': 'Europa Conference League',
        'positions': range(6, 7),
        'color': '#00A652',
        'badge': 'UECL',
        'emoji': '🌟'
    },
    'relegation': {
        'name': 'Relegation',
        'positions': range(18, 21),
        'color': '#CC0000',
        'badge': 'REL',
        'emoji': '⬇️'
    }
}