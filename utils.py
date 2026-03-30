"""
Utils
Funciones de utilidad para el bot
"""

import difflib
from typing import Optional


# Diccionario de aliases comunes para equipos
TEAM_ALIASES = {
    # Premier League
    'man city': 'manchester city',
    'man utd': 'manchester united',
    'man united': 'manchester united',
    'spurs': 'tottenham',

    # La Liga
    'barça': 'barcelona',
    'barca': 'barcelona',
    'real': 'real madrid',
    'atletico': 'atletico madrid',
    'atleti': 'atletico madrid',

    # Serie A
    'juve': 'juventus',
    'inter': 'inter milan',
    'milan': 'ac milan',

    # Bundesliga
    'bayern': 'bayern munich',
    'dortmund': 'borussia dortmund',
    'leverkusen': 'bayer leverkusen',
    'leipzig': 'rb leipzig',

    # Ligue 1
    'psg': 'paris saint-germain',

    # Argentina
    'boca': 'boca juniors',
    'river': 'river plate',

    # Otros
    'ajax': 'ajax amsterdam',
    'porto': 'fc porto',
    'benfica': 'sl benfica',
    'sporting': 'sporting cp',
}


# Lista de equipos conocidos para fuzzy matching
KNOWN_TEAMS = [
    # Selecciones
    'argentina', 'brazil', 'france', 'england', 'spain', 'germany',
    'netherlands', 'portugal', 'belgium', 'italy', 'colombia', 'uruguay',
    'mexico', 'usa', 'chile', 'ecuador', 'peru', 'paraguay',

    # Premier League
    'manchester city', 'liverpool', 'arsenal', 'chelsea', 'manchester united',
    'tottenham', 'newcastle', 'aston villa', 'brighton', 'west ham',
    'crystal palace', 'fulham', 'brentford', 'everton', 'wolves',
    'bournemouth', 'nottingham forest', 'luton town', 'burnley', 'sheffield united',

    # La Liga
    'real madrid', 'barcelona', 'atletico madrid', 'sevilla', 'real sociedad',
    'villarreal', 'athletic bilbao', 'real betis', 'valencia', 'osasuna',
    'getafe', 'girona', 'rayo vallecano', 'celta vigo', 'mallorca',
    'las palmas', 'cadiz', 'almeria', 'granada', 'alaves',

    # Bundesliga
    'bayern munich', 'borussia dortmund', 'rb leipzig', 'bayer leverkusen',
    'eintracht frankfurt', 'union berlin', 'freiburg', 'wolfsburg',
    'borussia monchengladbach', 'hoffenheim', 'mainz', 'koln',
    'werder bremen', 'augsburg', 'stuttgart', 'bochum', 'heidenheim', 'darmstadt',

    # Serie A
    'inter milan', 'ac milan', 'juventus', 'napoli', 'roma', 'lazio',
    'atalanta', 'fiorentina', 'torino', 'bologna', 'sassuolo',
    'udinese', 'monza', 'verona', 'cagliari', 'lecce', 'empoli',
    'frosinone', 'genoa', 'salernitana',

    # Ligue 1
    'paris saint-germain', 'monaco', 'marseille', 'lyon', 'lille',
    'nice', 'lens', 'rennes', 'strasbourg', 'toulouse',
    'montpellier', 'nantes', 'reims', 'brest', 'lorient',
    'le havre', 'metz', 'clermont', 'ajaccio',

    # Argentina
    'boca juniors', 'river plate', 'racing club', 'independiente',
    'san lorenzo', 'estudiantes', 'velez sarsfield', 'huracan',

    # Brazil
    'flamengo', 'palmeiras', 'corinthians', 'sao paulo', 'santos',
    'atletico mineiro', 'gremio', 'internacional',

    # Otros clubes importantes
    'ajax amsterdam', 'psv eindhoven', 'feyenoord',
    'fc porto', 'benfica', 'sporting cp',
    'celtic', 'rangers',
]


def normalize_team_name(input_name: str) -> str:
    """
    Normalizar nombre de equipo usando aliases y fuzzy matching

    Args:
        input_name: Nombre del equipo como lo escribió el usuario

    Returns:
        Nombre normalizado del equipo
    """
    if not input_name:
        return input_name

    # Limpiar y convertir a minúsculas
    normalized = input_name.strip().lower()

    # 1. Verificar aliases exactos primero
    if normalized in TEAM_ALIASES:
        return TEAM_ALIASES[normalized]

    # 2. Buscar coincidencias parciales en aliases (por si escriben "man city fc")
    for alias, full_name in TEAM_ALIASES.items():
        if alias in normalized or normalized in alias:
            return full_name

    # 3. Si ya está en la lista de equipos conocidos, retornar como está
    if normalized in KNOWN_TEAMS:
        return normalized

    # 4. Fuzzy matching contra equipos conocidos
    # cutoff=0.6 significa 60% de similitud mínima
    close_matches = difflib.get_close_matches(
        normalized,
        KNOWN_TEAMS,
        n=1,  # Solo la mejor coincidencia
        cutoff=0.6
    )

    if close_matches:
        return close_matches[0]

    # 5. Si no hay coincidencias, retornar el nombre original normalizado
    return normalized


def parse_team_names(full_text: str, separator: str = 'vs') -> tuple[Optional[str], Optional[str]]:
    """
    Parsear y normalizar nombres de dos equipos desde un texto

    Args:
        full_text: Texto completo con formato "equipo1 vs equipo2"
        separator: Separador entre equipos (default: 'vs')

    Returns:
        Tuple con (equipo1_normalizado, equipo2_normalizado)
        Retorna (None, None) si no se pueden parsear
    """
    # Intentar con variaciones comunes (case insensitive)
    parts = None

    for sep_variant in [' vs ', ' VS ', ' Vs ', ' vS ', ' v ', ' V ']:
        if sep_variant in full_text:
            parts = full_text.split(sep_variant, 1)
            break

    if not parts or len(parts) != 2:
        return None, None

    # Normalizar ambos equipos
    team1 = normalize_team_name(parts[0].strip())
    team2 = normalize_team_name(parts[1].strip())

    return team1, team2


def format_team_name(team_name: str) -> str:
    """
    Formatear nombre de equipo para mostrar (capitalizar correctamente)

    Args:
        team_name: Nombre del equipo en minúsculas

    Returns:
        Nombre capitalizado correctamente
    """
    # Palabras que deben ir en minúsculas (excepto al inicio)
    lowercase_words = {'de', 'del', 'la', 'el', 'los', 'las', 'y', 'e', 'o', 'u'}

    # Casos especiales que necesitan capitalización específica
    special_cases = {
        'ac milan': 'AC Milan',
        'fc porto': 'FC Porto',
        'psg': 'PSG',
        'ajax amsterdam': 'Ajax Amsterdam',
        'psv eindhoven': 'PSV Eindhoven',
        'rb leipzig': 'RB Leipzig',
        'usa': 'USA',
    }

    team_lower = team_name.lower()

    # Verificar casos especiales primero
    if team_lower in special_cases:
        return special_cases[team_lower]

    # Capitalizar cada palabra
    words = team_name.split()
    formatted_words = []

    for i, word in enumerate(words):
        if i == 0 or word.lower() not in lowercase_words:
            formatted_words.append(word.capitalize())
        else:
            formatted_words.append(word.lower())

    return ' '.join(formatted_words)
