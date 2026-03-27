"""
API Integrations
Integraciones con APIs externas de fútbol
"""

import os
import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class FootballAPIManager:
    """Gestor de múltiples APIs de fútbol"""

    def __init__(self):
        """Inicializar con API keys desde .env"""
        self.api_football_key = os.getenv('API_FOOTBALL_KEY', '')
        self.odds_api_key = os.getenv('ODDS_API_KEY', '')
        self.football_data_key = os.getenv('FOOTBALL_DATA_KEY', '')

    def get_upcoming_matches_api_football(self, days: int = 7) -> List[Dict]:
        """
        Obtener partidos próximos desde API-Football
        Free tier: 100 requests/día

        Args:
            days: Días hacia adelante

        Returns:
            Lista de partidos
        """
        if not self.api_football_key:
            logger.warning("API_FOOTBALL_KEY no configurada")
            return []

        try:
            headers = {
                'x-apisports-key': self.api_football_key
            }

            # Ligas principales (IDs de API-Football)
            leagues = {
                140: 'La Liga',
                39: 'Premier League',
                78: 'Bundesliga',
                135: 'Serie A',
                61: 'Ligue 1',
                128: 'Liga Profesional Argentina'
            }

            all_matches = []

            for league_id, league_name in leagues.items():
                # Obtener fixtures de los próximos días
                today = datetime.now()
                end_date = today + timedelta(days=days)

                url = "https://v3.football.api-sports.io/fixtures"
                params = {
                    'league': league_id,
                    'season': today.year,
                    'from': today.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d')
                }

                response = requests.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    if data.get('response'):
                        for match in data['response'][:10]:  # Limitar a 10 por liga
                            fixture = match.get('fixture', {})
                            teams = match.get('teams', {})
                            league_info = match.get('league', {})

                            match_data = {
                                'source': 'API-Football',
                                'league': league_name,
                                'date': fixture.get('date', ''),
                                'home_team': teams.get('home', {}).get('name', ''),
                                'away_team': teams.get('away', {}).get('name', ''),
                                'venue': fixture.get('venue', {}).get('name', ''),
                                'referee': fixture.get('referee', ''),
                                'status': fixture.get('status', {}).get('long', ''),
                            }

                            all_matches.append(match_data)

                logger.info(f"✓ Obtenidos partidos de {league_name}")

            return all_matches

        except Exception as e:
            logger.error(f"Error obteniendo partidos de API-Football: {e}")
            return []

    def get_match_odds(self, home_team: str, away_team: str) -> Optional[Dict]:
        """
        Obtener cuotas de apuestas desde The Odds API

        Args:
            home_team: Equipo local
            away_team: Equipo visitante

        Returns:
            Diccionario con odds o None
        """
        if not self.odds_api_key:
            logger.info("ODDS_API_KEY no configurada - Sin odds disponibles")
            return None

        try:
            url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'eu',
                'markets': 'h2h,totals',
                'oddsFormat': 'decimal'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Buscar el partido específico
                for match in data:
                    home = match.get('home_team', '')
                    away = match.get('away_team', '')

                    if home_team.lower() in home.lower() or away_team.lower() in away.lower():
                        bookmakers = match.get('bookmakers', [])

                        if bookmakers:
                            odds_data = {
                                'home_win': None,
                                'draw': None,
                                'away_win': None,
                                'over_25': None,
                                'under_25': None,
                                'bookmaker': bookmakers[0].get('title', 'Unknown')
                            }

                            for market in bookmakers[0].get('markets', []):
                                if market.get('key') == 'h2h':
                                    for outcome in market.get('outcomes', []):
                                        name = outcome.get('name')
                                        price = outcome.get('price')

                                        if name == home:
                                            odds_data['home_win'] = price
                                        elif name == away:
                                            odds_data['away_win'] = price
                                        elif 'Draw' in name:
                                            odds_data['draw'] = price

                                elif market.get('key') == 'totals':
                                    for outcome in market.get('outcomes', []):
                                        name = outcome.get('name')
                                        price = outcome.get('price')

                                        if 'Over' in name:
                                            odds_data['over_25'] = price
                                        elif 'Under' in name:
                                            odds_data['under_25'] = price

                            return odds_data

            return None

        except Exception as e:
            logger.error(f"Error obteniendo odds: {e}")
            return None

    def get_team_form_fotmob(self, team_name: str) -> Optional[Dict]:
        """
        Obtener forma reciente desde FotMob
        Requiere: pip install pyfotmob

        Args:
            team_name: Nombre del equipo

        Returns:
            Diccionario con forma del equipo
        """
        try:
            # Importar dinámicamente
            try:
                from fotmob import Fotmob
            except ImportError:
                logger.info("pyfotmob no instalado - Forma de FotMob no disponible")
                return None

            fotmob = Fotmob()

            # Buscar equipo
            search = fotmob.search(team_name)

            if search and 'teams' in search:
                teams = search.get('teams', [])

                if teams:
                    team_id = teams[0].get('id')

                    # Obtener detalles del equipo
                    team_data = fotmob.get_team(team_id)

                    if team_data:
                        return {
                            'source': 'FotMob',
                            'team': teams[0].get('name'),
                            'form': team_data.get('form', []),
                            'rank': team_data.get('rank'),
                            'points': team_data.get('points')
                        }

            return None

        except Exception as e:
            logger.error(f"Error obteniendo forma de FotMob: {e}")
            return None


# Función auxiliar para calcular value bets
def calculate_value_bet(predicted_probability: float, odds: float) -> Dict:
    """
    Calcular si una apuesta tiene valor

    Args:
        predicted_probability: Probabilidad predicha (0-1)
        odds: Cuota decimal de la casa de apuestas

    Returns:
        Diccionario con análisis de valor
    """
    implied_probability = 1 / odds  # Probabilidad implícita de las odds
    expected_value = (predicted_probability * odds) - 1

    is_value = expected_value > 0

    return {
        'predicted_probability': round(predicted_probability * 100, 1),
        'implied_probability': round(implied_probability * 100, 1),
        'expected_value': round(expected_value * 100, 1),
        'is_value_bet': is_value,
        'recommendation': 'APOSTAR' if is_value else 'NO APOSTAR'
    }


if __name__ == '__main__':
    # Test de las APIs
    print("🧪 Testing API Integrations...\n")

    api_manager = FootballAPIManager()

    # Test: Obtener partidos próximos
    print("📅 Test: Partidos próximos (3 días)")
    matches = api_manager.get_upcoming_matches_api_football(days=3)

    if matches:
        print(f"✓ Encontrados {len(matches)} partidos")
        print(f"Ejemplo: {matches[0]['home_team']} vs {matches[0]['away_team']}")
    else:
        print("⚠️  No se encontraron partidos (puede que falta API key)")

    # Test: Value bet
    print("\n💰 Test: Cálculo de value bet")
    value = calculate_value_bet(predicted_probability=0.65, odds=1.75)
    print(f"Probabilidad predicha: {value['predicted_probability']}%")
    print(f"Probabilidad implícita (odds): {value['implied_probability']}%")
    print(f"Valor esperado: {value['expected_value']}%")
    print(f"Recomendación: {value['recommendation']}")
