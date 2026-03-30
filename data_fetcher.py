"""
Data Fetcher
Sistema de obtención de datos de equipos desde APIs externas con caché
"""

import os
import logging
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class DataFetcher:
    """Fetcher de datos de equipos con múltiples fuentes y caché"""

    def __init__(self):
        """Inicializar data fetcher"""
        self.api_football_key = os.getenv('API_FOOTBALL_KEY')
        self.football_data_key = os.getenv('FOOTBALL_DATA_KEY')
        self.odds_api_key = os.getenv('ODDS_API_KEY')

        # Caché en memoria con TTL 1 hora
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)

        # Caché específico para odds (TTL más corto: 10 minutos)
        self._odds_cache = {}
        self._odds_cache_ttl = timedelta(minutes=10)

        # Configurar fuente de datos
        self._configure_source()

    def _configure_source(self):
        """Configurar fuente de datos disponible"""
        if self.api_football_key:
            self.source = 'api-football'
            logger.info("DataFetcher using API-Football")
        elif self.football_data_key:
            self.source = 'football-data'
            logger.info("DataFetcher using football-data.org")
        else:
            self.source = 'fallback'
            logger.info("DataFetcher using fallback (hardcoded data)")

    def get_team_strength(self, team: str, league: str = None) -> Dict[str, int]:
        """
        Obtener fortaleza del equipo desde API o caché

        Args:
            team: Nombre del equipo
            league: Liga del equipo (opcional)

        Returns:
            Dict con attack, defense, form (valores 0-100)
        """
        # Normalizar nombre del equipo para caché
        cache_key = f"{team.lower()}:{league.lower() if league else 'unknown'}"

        # Verificar caché
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.debug(f"Cache hit for {team}")
            return cached

        # Intentar obtener de API
        result = None

        if self.source == 'api-football':
            result = self._fetch_from_api_football(team, league)
        elif self.source == 'football-data':
            result = self._fetch_from_football_data(team, league)

        # Si API falló o no hay keys, usar fallback
        if not result:
            result = self._get_fallback_strength(team)

        # Guardar en caché
        self._save_to_cache(cache_key, result)

        return result

    def _get_from_cache(self, key: str) -> Optional[Dict[str, int]]:
        """Obtener datos del caché si no han expirado"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                return data
            else:
                # Caché expirado, eliminar
                del self._cache[key]
        return None

    def _save_to_cache(self, key: str, data: Dict[str, int]):
        """Guardar datos en caché con timestamp"""
        self._cache[key] = (data, datetime.now())

    def _fetch_from_api_football(self, team: str, league: str = None) -> Optional[Dict[str, int]]:
        """
        Obtener datos desde API-Football

        API-Football endpoint: /teams/statistics
        Requiere: team_id, league_id, season
        """
        try:
            # Nota: Esta es una implementación simplificada
            # En producción, necesitarías:
            # 1. Buscar team_id por nombre
            # 2. Buscar league_id por nombre
            # 3. Obtener season actual
            # 4. Llamar a /teams/statistics

            # Por ahora, retornamos None para usar fallback
            # TODO: Implementar llamada real a API-Football cuando tengas team_id
            logger.debug(f"API-Football fetch not fully implemented for {team}")
            return None

        except Exception as e:
            logger.error(f"Error fetching from API-Football: {e}")
            return None

    def _fetch_from_football_data(self, team: str, league: str = None) -> Optional[Dict[str, int]]:
        """
        Obtener datos desde football-data.org

        football-data.org tiene estadísticas de equipos pero requiere
        mapping de nombres a IDs
        """
        try:
            # Nota: Esta es una implementación simplificada
            # En producción, necesitarías:
            # 1. Buscar team_id por nombre
            # 2. Llamar a /teams/{id} para obtener stats

            # Por ahora, retornamos None para usar fallback
            # TODO: Implementar llamada real a football-data.org
            logger.debug(f"football-data.org fetch not fully implemented for {team}")
            return None

        except Exception as e:
            logger.error(f"Error fetching from football-data.org: {e}")
            return None

    def _get_fallback_strength(self, team: str) -> Dict[str, int]:
        """
        Fallback: usar diccionario hardcodeado (sin random)

        Returns:
            Dict con attack, defense, form
        """
        # Dict hardcodeado de equipos conocidos
        top_teams = {
            # Selecciones TOP
            'argentina': {'attack': 90, 'defense': 85, 'form': 88},
            'brazil': {'attack': 88, 'defense': 82, 'form': 85},
            'france': {'attack': 92, 'defense': 88, 'form': 90},
            'england': {'attack': 85, 'defense': 83, 'form': 82},
            'spain': {'attack': 87, 'defense': 85, 'form': 86},
            'germany': {'attack': 86, 'defense': 84, 'form': 84},
            'netherlands': {'attack': 84, 'defense': 80, 'form': 83},
            'portugal': {'attack': 85, 'defense': 78, 'form': 82},
            'belgium': {'attack': 83, 'defense': 79, 'form': 80},
            'italy': {'attack': 80, 'defense': 88, 'form': 81},
            'colombia': {'attack': 82, 'defense': 78, 'form': 80},
            'uruguay': {'attack': 81, 'defense': 82, 'form': 79},
            'mexico': {'attack': 75, 'defense': 72, 'form': 74},
            'usa': {'attack': 73, 'defense': 70, 'form': 72},
            'chile': {'attack': 74, 'defense': 73, 'form': 71},

            # Clubes TOP - Premier League
            'manchester city': {'attack': 95, 'defense': 88, 'form': 92},
            'man city': {'attack': 95, 'defense': 88, 'form': 92},
            'liverpool': {'attack': 89, 'defense': 84, 'form': 87},
            'arsenal': {'attack': 87, 'defense': 85, 'form': 86},
            'chelsea': {'attack': 84, 'defense': 82, 'form': 83},
            'manchester united': {'attack': 83, 'defense': 80, 'form': 81},
            'man united': {'attack': 83, 'defense': 80, 'form': 81},
            'tottenham': {'attack': 82, 'defense': 78, 'form': 80},
            'spurs': {'attack': 82, 'defense': 78, 'form': 80},
            'newcastle': {'attack': 79, 'defense': 81, 'form': 78},
            'aston villa': {'attack': 78, 'defense': 77, 'form': 77},

            # La Liga
            'real madrid': {'attack': 93, 'defense': 85, 'form': 90},
            'barcelona': {'attack': 90, 'defense': 82, 'form': 88},
            'atletico madrid': {'attack': 82, 'defense': 86, 'form': 83},
            'atletico': {'attack': 82, 'defense': 86, 'form': 83},
            'sevilla': {'attack': 78, 'defense': 79, 'form': 76},
            'real sociedad': {'attack': 77, 'defense': 76, 'form': 75},
            'villarreal': {'attack': 76, 'defense': 77, 'form': 74},
            'athletic bilbao': {'attack': 75, 'defense': 78, 'form': 74},
            'athletic': {'attack': 75, 'defense': 78, 'form': 74},

            # Bundesliga
            'bayern munich': {'attack': 92, 'defense': 86, 'form': 89},
            'bayern': {'attack': 92, 'defense': 86, 'form': 89},
            'borussia dortmund': {'attack': 86, 'defense': 79, 'form': 84},
            'dortmund': {'attack': 86, 'defense': 79, 'form': 84},
            'rb leipzig': {'attack': 83, 'defense': 81, 'form': 82},
            'leipzig': {'attack': 83, 'defense': 81, 'form': 82},
            'bayer leverkusen': {'attack': 82, 'defense': 80, 'form': 81},
            'leverkusen': {'attack': 82, 'defense': 80, 'form': 81},

            # Serie A
            'inter milan': {'attack': 85, 'defense': 88, 'form': 84},
            'inter': {'attack': 85, 'defense': 88, 'form': 84},
            'ac milan': {'attack': 83, 'defense': 82, 'form': 81},
            'milan': {'attack': 83, 'defense': 82, 'form': 81},
            'juventus': {'attack': 81, 'defense': 85, 'form': 80},
            'napoli': {'attack': 84, 'defense': 80, 'form': 82},
            'roma': {'attack': 79, 'defense': 78, 'form': 77},
            'lazio': {'attack': 78, 'defense': 77, 'form': 76},
            'atalanta': {'attack': 82, 'defense': 75, 'form': 79},

            # Ligue 1
            'psg': {'attack': 88, 'defense': 80, 'form': 83},
            'paris saint-germain': {'attack': 88, 'defense': 80, 'form': 83},
            'monaco': {'attack': 80, 'defense': 76, 'form': 77},
            'marseille': {'attack': 78, 'defense': 77, 'form': 76},
            'lyon': {'attack': 77, 'defense': 75, 'form': 75},
            'lille': {'attack': 76, 'defense': 78, 'form': 74},

            # Otros clubes importantes
            'ajax': {'attack': 79, 'defense': 74, 'form': 76},
            'benfica': {'attack': 80, 'defense': 76, 'form': 77},
            'porto': {'attack': 78, 'defense': 77, 'form': 76},
            'sporting': {'attack': 77, 'defense': 75, 'form': 75},
        }

        team_lower = team.lower()

        # Buscar equipo conocido (coincidencia parcial)
        for known_team, stats in top_teams.items():
            if known_team in team_lower or team_lower in known_team:
                logger.debug(f"Fallback match found for {team}: {known_team}")
                return stats.copy()

        # Equipo desconocido - valores predeterminados (sin random)
        # Usamos valores medios conservadores
        logger.debug(f"Unknown team {team}, using default values")
        return {
            'attack': 72,   # Valor medio-bajo fijo
            'defense': 72,  # Valor medio-bajo fijo
            'form': 72      # Valor medio-bajo fijo
        }

    def get_real_odds(self, home_team: str, away_team: str) -> Optional[Dict]:
        """
        Obtener odds reales desde The Odds API

        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante

        Returns:
            Dict con odds reales o None si no hay API key o no se encuentran
            Formato: {
                'home_win': float,
                'draw': float,
                'away_win': float,
                'over_25': float,
                'under_25': float,
                'btts_yes': float,
                'btts_no': float,
                'bookmaker': str
            }
        """
        # Sin API key, retornar None (NO inventar odds)
        if not self.odds_api_key:
            logger.debug("No ODDS_API_KEY configured, skipping real odds")
            return None

        # Normalizar nombres para cache key
        cache_key = f"odds:{home_team.lower()}:{away_team.lower()}"

        # Verificar caché de odds (TTL 10 minutos)
        if cache_key in self._odds_cache:
            data, timestamp = self._odds_cache[cache_key]
            if datetime.now() - timestamp < self._odds_cache_ttl:
                logger.debug(f"Odds cache hit for {home_team} vs {away_team}")
                return data

        try:
            # The Odds API - Soccer endpoint
            # Buscar en múltiples ligas comunes
            sport_keys = [
                'soccer_epl',  # Premier League
                'soccer_spain_la_liga',  # La Liga
                'soccer_germany_bundesliga',  # Bundesliga
                'soccer_italy_serie_a',  # Serie A
                'soccer_france_ligue_one',  # Ligue 1
                'soccer_uefa_champs_league',  # Champions
                'soccer_uefa_europa_league',  # Europa League
            ]

            for sport_key in sport_keys:
                url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
                params = {
                    'apiKey': self.odds_api_key,
                    'regions': 'eu,uk',  # Bookmakers europeos
                    'markets': 'h2h,totals,btts',  # h2h = 1X2, totals = Over/Under, btts = BTTS
                    'oddsFormat': 'decimal',
                }

                response = requests.get(url, params=params, timeout=5)

                if response.status_code != 200:
                    logger.debug(f"Odds API returned {response.status_code} for {sport_key}")
                    continue

                data = response.json()

                # Buscar el partido en los datos
                for game in data:
                    home = game.get('home_team', '').lower()
                    away = game.get('away_team', '').lower()

                    # Coincidencia parcial de nombres
                    if (home_team.lower() in home or home in home_team.lower()) and \
                       (away_team.lower() in away or away in away_team.lower()):

                        # Extraer odds del primer bookmaker disponible
                        bookmakers = game.get('bookmakers', [])
                        if not bookmakers:
                            continue

                        bookmaker = bookmakers[0]  # Usar primer bookmaker
                        bookmaker_name = bookmaker.get('title', 'Unknown')

                        odds_data = {
                            'bookmaker': bookmaker_name
                        }

                        # Extraer odds de cada mercado
                        for market in bookmaker.get('markets', []):
                            market_key = market.get('key')

                            if market_key == 'h2h':  # 1X2
                                outcomes = market.get('outcomes', [])
                                for outcome in outcomes:
                                    name = outcome.get('name', '')
                                    price = outcome.get('price', 0)

                                    if name == game.get('home_team'):
                                        odds_data['home_win'] = price
                                    elif name == game.get('away_team'):
                                        odds_data['away_win'] = price
                                    elif name.lower() == 'draw':
                                        odds_data['draw'] = price

                            elif market_key == 'totals':  # Over/Under
                                outcomes = market.get('outcomes', [])
                                for outcome in outcomes:
                                    name = outcome.get('name', '')
                                    point = outcome.get('point', 0)
                                    price = outcome.get('price', 0)

                                    # Buscar Over/Under 2.5
                                    if point == 2.5:
                                        if name.lower() == 'over':
                                            odds_data['over_25'] = price
                                        elif name.lower() == 'under':
                                            odds_data['under_25'] = price

                            elif market_key == 'btts':  # Both Teams To Score
                                outcomes = market.get('outcomes', [])
                                for outcome in outcomes:
                                    name = outcome.get('name', '')
                                    price = outcome.get('price', 0)

                                    if name.lower() == 'yes':
                                        odds_data['btts_yes'] = price
                                    elif name.lower() == 'no':
                                        odds_data['btts_no'] = price

                        # Verificar que tenemos al menos odds básicas (1X2)
                        if 'home_win' in odds_data and 'away_win' in odds_data:
                            logger.info(f"Real odds found for {home_team} vs {away_team} from {bookmaker_name}")

                            # Guardar en caché
                            self._odds_cache[cache_key] = (odds_data, datetime.now())

                            return odds_data

            # No se encontró el partido en ninguna liga
            logger.debug(f"No odds found for {home_team} vs {away_team}")
            return None

        except requests.RequestException as e:
            logger.error(f"Error fetching odds from The Odds API: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching odds: {e}")
            return None

    def clear_cache(self):
        """Limpiar toda la caché"""
        self._cache.clear()
        self._odds_cache.clear()
        logger.info("Cache cleared")

    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas de la caché"""
        now = datetime.now()
        valid_entries = sum(
            1 for _, (_, timestamp) in self._cache.items()
            if now - timestamp < self._cache_ttl
        )
        return {
            'total_entries': len(self._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(self._cache) - valid_entries,
            'ttl_hours': self._cache_ttl.total_seconds() / 3600
        }
