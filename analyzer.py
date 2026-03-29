"""
Soccer Data Analyzer
Analiza datos de fútbol y genera predicciones basadas en estadísticas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

try:
    import soccerdata as sd
except ImportError:
    print("⚠️  Instalando soccerdata...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'soccerdata'])
    import soccerdata as sd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SoccerAnalyzer:
    """Analizador de datos de fútbol para predicciones"""

    LEAGUES = {
        'ESP': 'La Liga',
        'ENG': 'Premier League',
        'GER': 'Bundesliga',
        'ITA': 'Serie A',
        'FRA': 'Ligue 1',
        'ARG': 'Liga Profesional'
    }

    # Competiciones de Selecciones Nacionales
    INTERNATIONAL_COMPETITIONS = {
        'WORLD_CUP': 'Copa del Mundo',
        'COPA_AMERICA': 'Copa América',
        'EURO': 'Eurocopa',
        'NATIONS_LEAGUE': 'UEFA Nations League',
        'FRIENDLIES': 'Amistosos Internacionales',
        'QUALIFIERS_UEFA': 'Eliminatorias UEFA',
        'QUALIFIERS_CONMEBOL': 'Eliminatorias CONMEBOL',
        'CONFEDERATIONS': 'Copa Confederaciones'
    }

    # Selecciones principales
    NATIONAL_TEAMS = {
        # Sudamérica
        'ARG': 'Argentina',
        'BRA': 'Brasil',
        'URU': 'Uruguay',
        'COL': 'Colombia',
        'CHI': 'Chile',
        'ECU': 'Ecuador',
        'PER': 'Perú',
        'PAR': 'Paraguay',
        # Europa
        'FRA': 'Francia',
        'ESP': 'España',
        'GER': 'Alemania',
        'ITA': 'Italia',
        'ENG': 'Inglaterra',
        'POR': 'Portugal',
        'BEL': 'Bélgica',
        'NED': 'Holanda',
        # Otras
        'USA': 'Estados Unidos',
        'MEX': 'México',
    }

    def __init__(self, cache_dir: str = './data'):
        """Inicializar analizador con caché de datos"""
        self.cache_dir = cache_dir
        self.fbref = None
        self.understat = None
        self._init_scrapers()

    def _init_scrapers(self):
        """Inicializar scrapers de datos"""
        try:
            logger.info("Inicializando scrapers de datos...")
            # FBref para estadísticas generales (más confiable)
            self.fbref = sd.FBref(leagues=list(self.LEAGUES.keys())[:5])  # Top 5 europeas
            logger.info("✓ FBref inicializado")

            # Understat para xG y estadísticas avanzadas
            understat_leagues = ['La Liga', 'EPL', 'Bundesliga', 'Serie A', 'Ligue 1']
            self.understat = sd.Understat(leagues=understat_leagues)
            logger.info("✓ Understat inicializado")

        except Exception as e:
            logger.error(f"Error inicializando scrapers: {e}")

    def get_team_stats(self, team_name: str, league: str = 'ENG', n_matches: int = 10) -> Dict:
        """
        Obtener estadísticas recientes de un equipo

        Args:
            team_name: Nombre del equipo
            league: Código de liga (ESP, ENG, etc.)
            n_matches: Número de partidos recientes a analizar

        Returns:
            Diccionario con estadísticas del equipo
        """
        try:
            logger.info(f"Obteniendo stats de {team_name}...")

            # Obtener temporada actual
            current_year = datetime.now().year
            season = f"{current_year-1}-{current_year}" if datetime.now().month < 8 else f"{current_year}-{current_year+1}"

            # Obtener datos de partidos
            schedule = self.fbref.read_schedule(league, season)

            # Filtrar partidos del equipo
            team_matches = schedule[
                (schedule['Home'] == team_name) |
                (schedule['Away'] == team_name)
            ].tail(n_matches)

            if team_matches.empty:
                return {'error': f'No se encontraron datos para {team_name}'}

            # Calcular estadísticas
            stats = self._calculate_team_stats(team_matches, team_name)

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {'error': str(e)}

    def _calculate_team_stats(self, matches: pd.DataFrame, team_name: str) -> Dict:
        """Calcular estadísticas del equipo"""

        stats = {
            'team': team_name,
            'matches_analyzed': len(matches),
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_scored': 0,
            'goals_conceded': 0,
            'clean_sheets': 0,
            'btts_count': 0,  # Both teams to score
            'over_25': 0,
            'over_35': 0,
        }

        for _, match in matches.iterrows():
            is_home = match.get('Home') == team_name

            try:
                if is_home:
                    goals_for = int(match.get('Score', '0-0').split('-')[0])
                    goals_against = int(match.get('Score', '0-0').split('-')[1])
                else:
                    goals_for = int(match.get('Score', '0-0').split('-')[1])
                    goals_against = int(match.get('Score', '0-0').split('-')[0])

                stats['goals_scored'] += goals_for
                stats['goals_conceded'] += goals_against

                total_goals = goals_for + goals_against

                # Resultados
                if goals_for > goals_against:
                    stats['wins'] += 1
                elif goals_for == goals_against:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1

                # Estadísticas adicionales
                if goals_against == 0:
                    stats['clean_sheets'] += 1

                if goals_for > 0 and goals_against > 0:
                    stats['btts_count'] += 1

                if total_goals > 2.5:
                    stats['over_25'] += 1

                if total_goals > 3.5:
                    stats['over_35'] += 1

            except (ValueError, AttributeError, IndexError):
                continue

        # Calcular promedios y porcentajes
        n = stats['matches_analyzed']
        if n > 0:
            stats['avg_goals_scored'] = round(stats['goals_scored'] / n, 2)
            stats['avg_goals_conceded'] = round(stats['goals_conceded'] / n, 2)
            stats['btts_percentage'] = round((stats['btts_count'] / n) * 100, 1)
            stats['over_25_percentage'] = round((stats['over_25'] / n) * 100, 1)
            stats['over_35_percentage'] = round((stats['over_35'] / n) * 100, 1)
            stats['clean_sheet_percentage'] = round((stats['clean_sheets'] / n) * 100, 1)
            stats['win_percentage'] = round((stats['wins'] / n) * 100, 1)

        return stats

    def predict_match(self, home_team: str, away_team: str, league: str = 'ENG') -> Dict:
        """
        Predecir resultado de un partido

        Args:
            home_team: Equipo local
            away_team: Equipo visitante
            league: Liga del partido

        Returns:
            Diccionario con predicciones y confianza
        """
        try:
            logger.info(f"Analizando {home_team} vs {away_team}...")

            # Obtener stats de ambos equipos
            home_stats = self.get_team_stats(home_team, league, n_matches=10)
            away_stats = self.get_team_stats(away_team, league, n_matches=10)

            if 'error' in home_stats or 'error' in away_stats:
                return {'error': 'No se pudieron obtener datos de los equipos'}

            # Generar predicciones
            predictions = self._generate_predictions(home_stats, away_stats)

            return {
                'match': f"{home_team} vs {away_team}",
                'home_stats': home_stats,
                'away_stats': away_stats,
                'predictions': predictions
            }

        except Exception as e:
            logger.error(f"Error prediciendo partido: {e}")
            return {'error': str(e)}

    def _generate_predictions(self, home: Dict, away: Dict) -> List[Dict]:
        """Generar predicciones basadas en estadísticas"""

        predictions = []

        # 1. Over 2.5 goles
        avg_total_goals = home['avg_goals_scored'] + away['avg_goals_scored']
        over_25_prob = (home['over_25_percentage'] + away['over_25_percentage']) / 2

        if avg_total_goals > 2.8 and over_25_prob > 60:
            confidence = min(95, int(over_25_prob))
            predictions.append({
                'type': 'Over 2.5 goles',
                'description': f'Se esperan más de 2.5 goles en el partido',
                'confidence': confidence,
                'reason': f'Promedio combinado: {avg_total_goals:.1f} goles. Histórico Over 2.5: {over_25_prob:.0f}%'
            })

        # 2. Ambos equipos marcan (BTTS)
        btts_prob = (home['btts_percentage'] + away['btts_percentage']) / 2

        if btts_prob > 55 and home['avg_goals_scored'] > 1 and away['avg_goals_scored'] > 0.8:
            confidence = min(90, int(btts_prob))
            predictions.append({
                'type': 'Ambos equipos marcan (BTTS)',
                'description': 'Ambos equipos anotarán al menos un gol',
                'confidence': confidence,
                'reason': f'BTTS en {btts_prob:.0f}% de partidos. Ambos equipos tienen buen ataque.'
            })

        # 3. Victoria del local (si es muy superior)
        if home['win_percentage'] > 60 and away['win_percentage'] < 40:
            goal_diff = home['avg_goals_scored'] - home['avg_goals_conceded']
            away_goal_diff = away['avg_goals_scored'] - away['avg_goals_conceded']

            if goal_diff > 0.8 and away_goal_diff < 0.3:
                confidence = min(80, int(home['win_percentage']))
                predictions.append({
                    'type': 'Victoria del local',
                    'description': f'{home["team"]} tiene ventaja clara',
                    'confidence': confidence,
                    'reason': f'Local: {home["win_percentage"]:.0f}% victorias. Diferencia de goles: +{goal_diff:.1f}'
                })

        # 4. Under 2.5 (si ambos son defensivos)
        if avg_total_goals < 2.0 and home['over_25_percentage'] < 40 and away['over_25_percentage'] < 40:
            confidence = 70
            predictions.append({
                'type': 'Under 2.5 goles',
                'description': 'Se esperan menos de 2.5 goles',
                'confidence': confidence,
                'reason': f'Promedio: {avg_total_goals:.1f} goles. Ambos equipos son defensivos.'
            })

        # 5. Córners (si hay datos de tiros)
        # Esto requeriría más datos de FBref, lo dejamos para expansión futura

        # Ordenar por confianza
        predictions.sort(key=lambda x: x['confidence'], reverse=True)

        return predictions

    def get_today_matches(self, leagues: List[str] = None) -> List[Dict]:
        """
        Obtener partidos de hoy con predicciones

        Args:
            leagues: Lista de códigos de liga (None = todas)

        Returns:
            Lista de partidos con predicciones
        """
        return self.get_matches_by_date(days_ahead=0, leagues=leagues)

    def get_upcoming_matches(self, days_ahead: int = 7, leagues: List[str] = None) -> List[Dict]:
        """
        Obtener partidos próximos con predicciones

        Args:
            days_ahead: Días hacia adelante (default: 7)
            leagues: Lista de códigos de liga (None = todas)

        Returns:
            Lista de partidos con predicciones
        """
        return self.get_matches_by_date(days_ahead=days_ahead, leagues=leagues)

    def get_matches_by_date(self, days_ahead: int = 0, leagues: List[str] = None) -> List[Dict]:
        """
        Obtener partidos por fecha con predicciones

        Args:
            days_ahead: Días hacia adelante desde hoy (0 = hoy, 7 = próxima semana)
            leagues: Lista de códigos de liga (None = todas)

        Returns:
            Lista de partidos con predicciones
        """
        if leagues is None:
            leagues = list(self.LEAGUES.keys())[:5]  # Top 5 europeas por defecto

        all_matches = []
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_ahead)

        try:
            # Primero intentar con API-Football si está disponible
            try:
                from api_integrations import FootballAPIManager

                api_manager = FootballAPIManager()

                # Si es hoy (days_ahead=0), obtener TODOS los partidos del día
                if days_ahead == 0:
                    api_matches = api_manager.get_all_matches_by_date()
                else:
                    # Para días futuros, usar el método con ligas específicas
                    api_matches = api_manager.get_upcoming_matches_api_football(days=days_ahead, include_international=True)

                if api_matches:
                    logger.info(f"✓ Usando API-Football: {len(api_matches)} partidos encontrados")

                    # Filtrar partidos relevantes (ligas importantes y selecciones)
                    relevant_keywords = [
                        'Premier', 'Liga', 'Bundesliga', 'Serie A', 'Ligue',
                        'Mundial', 'Copa', 'International', 'Friendlies', 'Amistosos', 'Friendly',
                        'Nations League', 'Euro', 'América', 'Eliminatorias', 'Qualifiers',
                        'Argentina', 'Brazil', 'Colombia', 'Uruguay', 'Chile', 'Peru', 'Ecuador',
                        'Spain', 'England', 'Germany', 'France', 'Italy', 'Portugal', 'Belgium',
                        'Netherlands', 'Croatia', 'Mexico', 'USA', 'Japan', 'Korea'
                    ]

                    for match in api_matches:
                        # Verificar si es un partido relevante
                        league_name = match.get('league', '').lower()
                        home = match.get('home_team', '').lower()
                        away = match.get('away_team', '').lower()

                        is_relevant = any(
                            keyword.lower() in league_name or
                            keyword.lower() in home or
                            keyword.lower() in away
                            for keyword in relevant_keywords
                        )

                        if is_relevant:
                            # Normalizar nombres de claves para compatibilidad con bot.py
                            normalized_match = {
                                'league': match.get('league', 'Unknown'),
                                'home': match.get('home_team', ''),
                                'away': match.get('away_team', ''),
                                'time': match.get('date', ''),
                                'timestamp': match.get('timestamp', 0),
                                'venue': match.get('venue', ''),
                                'status': match.get('status', 'Scheduled'),
                            }

                            # Generar predicciones reales usando el motor avanzado
                            try:
                                from prediction_engine import PredictionEngine
                                pred_engine = PredictionEngine()
                                analysis = pred_engine.analyze_match(
                                    normalized_match['home'],
                                    normalized_match['away'],
                                    normalized_match['league']
                                )
                                normalized_match['predictions'] = analysis.get('predictions', [])
                                normalized_match['analysis'] = analysis
                            except Exception as e:
                                logger.warning(f"Error generando predicción: {e}")
                                normalized_match['predictions'] = [{
                                    'type': 'Info',
                                    'description': f"Análisis disponible pronto",
                                    'confidence': 0
                                }]

                            all_matches.append(normalized_match)

                    if all_matches:
                        # Ordenar por timestamp
                        all_matches.sort(key=lambda x: x.get('timestamp', 0))
                        logger.info(f"✓ {len(all_matches)} partidos relevantes después de filtrado")
                        return all_matches[:30]  # Limitar a 30 partidos

            except ImportError:
                logger.info("API-Football no disponible, usando FBref...")
            except Exception as e:
                logger.warning(f"Error con API-Football: {e}, fallback a FBref")

            # Fallback: Usar FBref
            for league in leagues:
                logger.info(f"Buscando partidos en {self.LEAGUES.get(league, league)}...")

                current_year = datetime.now().year
                season = f"{current_year-1}-{current_year}" if datetime.now().month < 8 else f"{current_year}-{current_year+1}"

                try:
                    schedule = self.fbref.read_schedule(league, season)

                    # Filtrar partidos por rango de fechas
                    schedule['Date'] = pd.to_datetime(schedule['Date'], errors='coerce')

                    if days_ahead == 0:
                        # Solo hoy
                        filtered_games = schedule[schedule['Date'].dt.date == start_date]
                    else:
                        # Rango de fechas
                        filtered_games = schedule[
                            (schedule['Date'].dt.date >= start_date) &
                            (schedule['Date'].dt.date <= end_date)
                        ]

                    for _, match in filtered_games.iterrows():
                        home = match.get('Home', '')
                        away = match.get('Away', '')

                        if home and away:
                            prediction = self.predict_match(home, away, league)

                            if 'error' not in prediction:
                                match_date = match.get('Date')
                                all_matches.append({
                                    'source': 'FBref',
                                    'league': self.LEAGUES.get(league, league),
                                    'date': match_date.strftime('%Y-%m-%d') if pd.notna(match_date) else 'TBD',
                                    'home': home,
                                    'away': away,
                                    'time': match.get('Time', 'TBD'),
                                    'predictions': prediction.get('predictions', [])
                                })

                except Exception as e:
                    logger.warning(f"No se pudieron obtener partidos de {league}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error obteniendo partidos: {e}")

        return all_matches

    def predict_international_match(self, team1: str, team2: str, competition: str = 'FRIENDLIES') -> Dict:
        """
        Predecir partido de selecciones nacionales

        Args:
            team1: Primera selección (ej: 'Argentina')
            team2: Segunda selección (ej: 'Brasil')
            competition: Tipo de competición

        Returns:
            Diccionario con predicciones
        """
        try:
            logger.info(f"🌍 Analizando partido internacional: {team1} vs {team2}")

            # Para selecciones usamos análisis simplificado basado en ranking FIFA
            # y datos históricos (FBref tiene datos limitados de selecciones)

            comp_name = self.INTERNATIONAL_COMPETITIONS.get(competition, 'Amistoso Internacional')

            # Análisis básico - en el futuro se puede mejorar con más fuentes
            prediction = {
                'match': f"{team1} vs {team2}",
                'competition': comp_name,
                'predictions': []
            }

            # Patrones generales para selecciones
            if competition in ['WORLD_CUP', 'COPA_AMERICA', 'EURO']:
                # Torneos importantes: más defensivos
                prediction['predictions'].append({
                    'type': 'Partido cerrado',
                    'description': 'Los partidos de torneo suelen ser más tácticos',
                    'confidence': 70,
                    'reason': 'Torneos importantes tienden a ser más conservadores'
                })

                prediction['predictions'].append({
                    'type': 'Under 2.5 goles',
                    'description': 'Se esperan pocos goles',
                    'confidence': 65,
                    'reason': 'En eliminación directa los equipos son más precavidos'
                })

            elif competition == 'FRIENDLIES':
                # Amistosos: más abiertos
                prediction['predictions'].append({
                    'type': 'Over 2.5 goles',
                    'description': 'Los amistosos suelen ser más abiertos',
                    'confidence': 68,
                    'reason': 'Amistosos tienen menos presión, equipos juegan más ofensivos'
                })

                prediction['predictions'].append({
                    'type': 'BTTS (Ambos marcan)',
                    'description': 'Ambos equipos probablemente anoten',
                    'confidence': 65,
                    'reason': 'Amistosos permiten experimentar y rotar jugadores'
                })

            elif competition in ['QUALIFIERS_UEFA', 'QUALIFIERS_CONMEBOL']:
                # Eliminatorias: depende del local
                prediction['predictions'].append({
                    'type': 'Victoria del local',
                    'description': 'El local tiene ventaja en eliminatorias',
                    'confidence': 72,
                    'reason': 'Localía es factor decisivo en eliminatorias'
                })

            # Nota especial
            prediction['note'] = (
                "⚠️ Nota: Los datos de selecciones son limitados. "
                "Las predicciones se basan en patrones históricos generales. "
                "Para el Mundial 2026 tendremos más datos y mejores predicciones."
            )

            return prediction

        except Exception as e:
            logger.error(f"Error prediciendo partido internacional: {e}")
            return {'error': str(e)}

    def get_trending_patterns(self, min_confidence: int = 75) -> List[Dict]:
        """
        Obtener patrones estadísticos más confiables

        Args:
            min_confidence: Confianza mínima para incluir el patrón

        Returns:
            Lista de patrones con alta confianza
        """
        patterns = [
            {
                'pattern': 'Over 2.5 en partidos de equipos top',
                'description': 'Cuando 2 equipos del top 6 se enfrentan',
                'confidence': 78,
                'applies_to': ['Premier League', 'La Liga']
            },
            {
                'pattern': 'BTTS en derbis',
                'description': 'Ambos equipos marcan en rivalidades locales',
                'confidence': 82,
                'applies_to': ['Todas las ligas']
            },
            {
                'pattern': 'Over 3.5 córners por equipo',
                'description': 'Equipos con >70% posesión vs equipos defensivos',
                'confidence': 76,
                'applies_to': ['Premier League', 'Bundesliga']
            },
            {
                'pattern': 'Local gana cuando viene de 3+ victorias',
                'description': 'Ventaja de local aumenta con racha positiva',
                'confidence': 74,
                'applies_to': ['Todas las ligas']
            }
        ]

        return [p for p in patterns if p['confidence'] >= min_confidence]


# Función de utilidad para formatear predicciones
def format_prediction(prediction: Dict) -> str:
    """Formatear predicción para mostrar en Telegram"""

    if 'error' in prediction:
        return f"❌ Error: {prediction['error']}"

    output = []
    output.append(f"⚽ *{prediction['match']}*\n")

    if 'predictions' in prediction and prediction['predictions']:
        output.append("📊 *Predicciones:*\n")

        for i, pred in enumerate(prediction['predictions'][:3], 1):  # Top 3
            confidence_emoji = "🔥" if pred['confidence'] >= 80 else "✅" if pred['confidence'] >= 70 else "⚠️"

            output.append(f"{confidence_emoji} *{pred['type']}* ({pred['confidence']}% confianza)")
            output.append(f"   └ {pred['description']}")
            output.append(f"   └ _Razón: {pred['reason']}_\n")
    else:
        output.append("⚠️ No hay predicciones con suficiente confianza para este partido.\n")

    return '\n'.join(output)


if __name__ == '__main__':
    # Test del analizador
    print("🔍 Iniciando Soccer Analyzer...")

    analyzer = SoccerAnalyzer()

    # Test: Analizar un equipo
    print("\n📊 Test: Estadísticas de Manchester City")
    stats = analyzer.get_team_stats("Manchester City", "ENG")
    print(stats)

    # Test: Predecir un partido
    print("\n🎯 Test: Predicción Manchester City vs Liverpool")
    prediction = analyzer.predict_match("Manchester City", "Liverpool", "ENG")
    print(format_prediction(prediction))
