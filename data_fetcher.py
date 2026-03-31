"""
Data Fetcher - football-data.org API
Sistema de obtención de datos reales desde football-data.org
"""

import os
import time
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class DataFetcher:
    """Fetcher de datos desde football-data.org con caché"""

    BASE_URL = "https://api.football-data.org/v4"

    # Mapeo de códigos de competición
    COMPETITIONS = {
        'PL': 2021,   # Premier League
        'PD': 2014,   # La Liga
        'BL1': 2002,  # Bundesliga
        'SA': 2019,   # Serie A
        'FL1': 2015,  # Ligue 1
        'CL': 2001,   # Champions League
        'WC': 2000,   # World Cup
    }

    def __init__(self):
        """Inicializar data fetcher con API keys"""
        # football-data.org API
        self.api_key = os.getenv('FOOTBALL_DATA_KEY')
        if not self.api_key:
            raise ValueError("FOOTBALL_DATA_KEY no encontrada en .env")

        self.headers = {
            'X-Auth-Token': self.api_key
        }

        # The Odds API
        self.odds_api_key = os.getenv('ODDS_API_KEY')
        self.odds_base_url = "https://api.the-odds-api.com/v4"
        self.odds_requests_remaining = None  # Trackear requests restantes

        # Caché en memoria con TTL 1 hora
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)

        logger.info("DataFetcher inicializado con football-data.org API")
        if self.odds_api_key:
            logger.info("The Odds API key configurada")
        else:
            logger.warning("ODDS_API_KEY no encontrada - odds reales no disponibles")

    def _get_from_cache(self, key: str) -> Optional[any]:
        """Obtener datos del caché si no han expirado"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                logger.debug(f"Cache HIT: {key}")
                return data
            else:
                del self._cache[key]
                logger.debug(f"Cache EXPIRED: {key}")
        return None

    def _save_to_cache(self, key: str, data: any):
        """Guardar datos en caché con timestamp"""
        self._cache[key] = (data, datetime.now())
        logger.debug(f"Cache SAVED: {key}")

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Hacer request a la API con manejo de rate limit

        Args:
            endpoint: Endpoint de la API (ej: /competitions)
            params: Parámetros de query

        Returns:
            Respuesta JSON o None si error
        """
        url = f"{self.BASE_URL}{endpoint}"
        logger.info(f"API REQUEST: {url} | params: {params}")

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            logger.info(f"API RESPONSE: {response.status_code} | {url}")

            # Rate limit: esperar y reintentar
            if response.status_code == 429:
                logger.warning("Rate limit 429 - Esperando 60 segundos...")
                time.sleep(60)

                # Reintentar una vez
                logger.info(f"API RETRY: {url}")
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                logger.info(f"API RETRY RESPONSE: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                logger.info(f"API SUCCESS: {len(str(data))} bytes received")
                return data
            else:
                logger.error(f"API ERROR: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"REQUEST EXCEPTION: {e}")
            return None

    def get_competitions(self) -> List[Dict]:
        """
        Obtener lista de competiciones disponibles

        Returns:
            Lista de diccionarios con id, name, code, area
        """
        cache_key = "competitions"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        data = self._make_request("/competitions")
        if not data or 'competitions' not in data:
            logger.warning("No se pudieron obtener competiciones")
            return []

        competitions = []
        for comp in data['competitions']:
            competitions.append({
                'id': comp['id'],
                'name': comp['name'],
                'code': comp.get('code', 'N/A'),
                'area': comp['area']['name'],
                'type': comp.get('type', 'LEAGUE')
            })

        self._save_to_cache(cache_key, competitions)
        logger.info(f"Competiciones obtenidas: {len(competitions)}")
        return competitions

    def get_team_id(self, team_name: str, competition_id: int) -> Optional[int]:
        """
        Buscar team_id por nombre usando fuzzy matching

        Args:
            team_name: Nombre del equipo a buscar
            competition_id: ID de la competición

        Returns:
            Team ID o None si no encuentra
        """
        cache_key = f"teams_comp_{competition_id}"
        cached = self._get_from_cache(cache_key)

        if not cached:
            data = self._make_request(f"/competitions/{competition_id}/teams")
            if not data or 'teams' not in data:
                logger.warning(f"No se pudieron obtener equipos de competición {competition_id}")
                return None
            cached = data['teams']
            self._save_to_cache(cache_key, cached)

        # Fuzzy matching con difflib
        best_match = None
        best_ratio = 0.0

        team_name_lower = team_name.lower()

        for team in cached:
            # Comparar nombre completo
            name_lower = team['name'].lower()
            ratio = SequenceMatcher(None, team_name_lower, name_lower).ratio()

            # También comparar short name si existe
            short_name = team.get('shortName', '').lower()
            short_ratio = SequenceMatcher(None, team_name_lower, short_name).ratio()

            # TLA (three letter acronym)
            tla = team.get('tla', '').lower()
            tla_ratio = SequenceMatcher(None, team_name_lower, tla).ratio()

            max_ratio = max(ratio, short_ratio, tla_ratio)

            if max_ratio > best_ratio:
                best_ratio = max_ratio
                best_match = team

        if best_match and best_ratio > 0.6:  # Threshold 60%
            logger.info(f"Team match: '{team_name}' -> '{best_match['name']}' (ratio: {best_ratio:.2f})")
            return best_match['id']

        logger.warning(f"No se encontró equipo para '{team_name}' (best ratio: {best_ratio:.2f})")
        return None

    def get_team_stats(self, team_id: int, season: int = None) -> Dict:
        """
        Obtener estadísticas calculadas de últimos 10 partidos

        Args:
            team_id: ID del equipo
            season: Año de la temporada (default: año actual, intenta anterior si falla)

        Returns:
            Dict con attack, defense, form (0-100), recent_matches
        """
        if season is None:
            season = datetime.now().year

        cache_key = f"team_stats_{team_id}_{season}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        # Obtener partidos del equipo (terminados)
        data = self._make_request(
            f"/teams/{team_id}/matches",
            params={'season': season, 'status': 'FINISHED'}
        )

        # Si no hay datos, intentar con temporada anterior
        if (not data or 'matches' not in data or len(data['matches']) == 0) and season == datetime.now().year:
            logger.info(f"No hay datos para {season}, intentando con {season-1}")
            season = season - 1
            data = self._make_request(
                f"/teams/{team_id}/matches",
                params={'season': season, 'status': 'FINISHED'}
            )

        if not data or 'matches' not in data:
            logger.warning(f"No se pudieron obtener partidos del equipo {team_id}")
            return {
                'attack': 70,
                'defense': 70,
                'form': 70,
                'recent_matches': [],
                'total_matches': 0
            }

        matches = data['matches'][:10]  # Últimos 10 partidos

        if not matches:
            return {
                'attack': 70,
                'defense': 70,
                'form': 70,
                'recent_matches': [],
                'total_matches': 0
            }

        # Calcular estadísticas
        total_goals_for = 0
        total_goals_against = 0
        wins = 0
        draws = 0
        losses = 0

        recent_matches = []

        for match in matches:
            score = match.get('score', {}).get('fullTime', {})
            home_team_id = match['homeTeam']['id']
            away_team_id = match['awayTeam']['id']
            home_goals = score.get('home')
            away_goals = score.get('away')

            if home_goals is None or away_goals is None:
                continue

            is_home = (home_team_id == team_id)

            if is_home:
                goals_for = home_goals
                goals_against = away_goals
            else:
                goals_for = away_goals
                goals_against = home_goals

            total_goals_for += goals_for
            total_goals_against += goals_against

            # Resultado
            if goals_for > goals_against:
                wins += 1
                result = 'W'
            elif goals_for < goals_against:
                losses += 1
                result = 'L'
            else:
                draws += 1
                result = 'D'

            recent_matches.append({
                'opponent': match['awayTeam']['name'] if is_home else match['homeTeam']['name'],
                'result': result,
                'score': f"{goals_for}-{goals_against}",
                'home': is_home
            })

        total_matches = len(recent_matches)

        if total_matches == 0:
            return {
                'attack': 70,
                'defense': 70,
                'form': 70,
                'recent_matches': [],
                'total_matches': 0
            }

        # Calcular métricas (0-100)
        avg_goals_for = total_goals_for / total_matches
        avg_goals_against = total_goals_against / total_matches

        # Attack: basado en goles anotados (0-100)
        # 3+ goles por partido = 100, 0 goles = 0
        attack = min(100, int((avg_goals_for / 3.0) * 100))

        # Defense: basado en goles recibidos (invertido)
        # 0 goles en contra = 100, 3+ goles en contra = 0
        defense = max(0, 100 - int((avg_goals_against / 3.0) * 100))

        # Form: basado en puntos (3 por victoria, 1 por empate)
        points = (wins * 3) + draws
        max_points = total_matches * 3
        form = int((points / max_points) * 100)

        stats = {
            'attack': attack,
            'defense': defense,
            'form': form,
            'recent_matches': recent_matches,
            'total_matches': total_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': total_goals_for,
            'goals_against': total_goals_against
        }

        self._save_to_cache(cache_key, stats)
        logger.info(f"Stats calculadas para team {team_id}: ATK={attack} DEF={defense} FORM={form}")

        return stats

    def get_upcoming_matches(self, competition_id: int, days_ahead: int = 7) -> List[Dict]:
        """
        Obtener próximos partidos de una competición

        Args:
            competition_id: ID de la competición
            days_ahead: Días hacia adelante a buscar

        Returns:
            Lista de próximos partidos con home_team, away_team, date, matchday
        """
        cache_key = f"upcoming_{competition_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        data = self._make_request(
            f"/competitions/{competition_id}/matches",
            params={'status': 'SCHEDULED'}
        )

        if not data or 'matches' not in data:
            logger.warning(f"No se pudieron obtener próximos partidos de {competition_id}")
            return []

        upcoming = []
        from datetime import timezone
        now = datetime.now(timezone.utc)
        limit_date = now + timedelta(days=days_ahead)

        for match in data['matches']:
            match_date_str = match.get('utcDate')
            if not match_date_str:
                continue

            try:
                match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            except:
                continue

            # Filtrar por rango de fechas
            if match_date > limit_date:
                continue

            upcoming.append({
                'match_id': match['id'],
                'home_team': match['homeTeam']['name'],
                'home_team_id': match['homeTeam']['id'],
                'away_team': match['awayTeam']['name'],
                'away_team_id': match['awayTeam']['id'],
                'date': match_date.isoformat(),
                'matchday': match.get('matchday', 0),
                'competition': match['competition']['name']
            })

        self._save_to_cache(cache_key, upcoming)
        logger.info(f"Próximos partidos obtenidos: {len(upcoming)}")

        return upcoming

    def get_match_result(self, match_id: int) -> Optional[Dict]:
        """
        Obtener resultado de un partido específico

        Args:
            match_id: ID del partido

        Returns:
            Dict con resultado completo o None
        """
        cache_key = f"match_{match_id}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        data = self._make_request(f"/matches/{match_id}")

        if not data:
            logger.warning(f"No se pudo obtener partido {match_id}")
            return None

        score = data.get('score', {}).get('fullTime', {})
        home_goals = score.get('home')
        away_goals = score.get('away')

        result = {
            'match_id': match_id,
            'home_team': data['homeTeam']['name'],
            'away_team': data['awayTeam']['name'],
            'status': data['status'],
            'home_goals': home_goals,
            'away_goals': away_goals,
            'date': data.get('utcDate'),
            'competition': data['competition']['name']
        }

        # Solo cachear si el partido terminó
        if data['status'] == 'FINISHED' and home_goals is not None:
            self._save_to_cache(cache_key, result)

        logger.info(f"Resultado obtenido: {result['home_team']} {home_goals}-{away_goals} {result['away_team']}")

        return result

    def get_real_odds(self, home_team: str, away_team: str) -> Optional[Dict]:
        """
        Obtener odds reales desde The Odds API

        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante

        Returns:
            Dict con {home_win, draw, away_win, bookmaker, requests_remaining} o None
        """
        if not self.odds_api_key:
            logger.warning("ODDS_API_KEY no configurada - no se pueden obtener odds")
            return None

        # Verificar si ya agotamos el límite
        if self.odds_requests_remaining is not None and self.odds_requests_remaining < 50:
            logger.warning(f"⚠️ Solo quedan {self.odds_requests_remaining} requests - pausando obtención de odds")
            return None

        # Ligas a probar en orden
        leagues_to_try = [
            'soccer_epl',                    # Premier League
            'soccer_spain_la_liga',          # La Liga
            'soccer_germany_bundesliga',     # Bundesliga
            'soccer_italy_serie_a',          # Serie A
            'soccer_france_ligue_one',       # Ligue 1
            'soccer_uefa_champs_league'      # Champions League
        ]

        for league in leagues_to_try:
            logger.info(f"Buscando odds en {league} para {home_team} vs {away_team}")

            # Construir URL
            url = f"{self.odds_base_url}/sports/{league}/odds/"
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'eu',  # Bookmakers europeos
                'markets': 'h2h',  # Head to head (1X2)
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }

            try:
                response = requests.get(url, params=params, timeout=10)

                # Trackear requests remaining
                if 'x-requests-remaining' in response.headers:
                    self.odds_requests_remaining = int(response.headers['x-requests-remaining'])
                    logger.info(f"📊 The Odds API - Requests remaining: {self.odds_requests_remaining}")

                if response.status_code == 429:
                    logger.warning("Rate limit alcanzado en The Odds API")
                    return None

                if response.status_code != 200:
                    logger.warning(f"Error {response.status_code} en The Odds API para {league}")
                    continue

                data = response.json()

                # Buscar el partido usando fuzzy matching
                for event in data:
                    event_home = event.get('home_team', '')
                    event_away = event.get('away_team', '')

                    # Fuzzy match para ambos equipos
                    home_ratio = SequenceMatcher(None, home_team.lower(), event_home.lower()).ratio()
                    away_ratio = SequenceMatcher(None, away_team.lower(), event_away.lower()).ratio()

                    # Threshold 0.6 (60% similitud)
                    if home_ratio > 0.6 and away_ratio > 0.6:
                        logger.info(f"✓ Partido encontrado: {event_home} vs {event_away}")
                        logger.info(f"   Match ratios: home={home_ratio:.2f}, away={away_ratio:.2f}")

                        # Obtener odds del primer bookmaker disponible
                        bookmakers = event.get('bookmakers', [])
                        if not bookmakers:
                            logger.warning("No hay bookmakers disponibles para este partido")
                            return None

                        bookmaker = bookmakers[0]
                        bookmaker_name = bookmaker.get('key', 'unknown')

                        # Obtener mercado h2h (home/draw/away)
                        markets = bookmaker.get('markets', [])
                        h2h_market = None
                        for market in markets:
                            if market.get('key') == 'h2h':
                                h2h_market = market
                                break

                        if not h2h_market:
                            logger.warning("No se encontró mercado h2h")
                            return None

                        # Extraer odds
                        outcomes = h2h_market.get('outcomes', [])
                        odds_dict = {}
                        for outcome in outcomes:
                            name = outcome.get('name')
                            price = outcome.get('price')
                            if name == event_home:
                                odds_dict['home_win'] = price
                            elif name == event_away:
                                odds_dict['away_win'] = price
                            elif name == 'Draw':
                                odds_dict['draw'] = price

                        if 'home_win' in odds_dict and 'draw' in odds_dict and 'away_win' in odds_dict:
                            result = {
                                'home_win': odds_dict['home_win'],
                                'draw': odds_dict['draw'],
                                'away_win': odds_dict['away_win'],
                                'bookmaker': bookmaker_name,
                                'requests_remaining': self.odds_requests_remaining,
                                'league': league,
                                'event_home': event_home,
                                'event_away': event_away
                            }

                            logger.info(f"💰 Odds obtenidas: HOME={result['home_win']} DRAW={result['draw']} AWAY={result['away_win']} ({bookmaker_name})")
                            return result
                        else:
                            logger.warning("Odds incompletas para este partido")
                            return None

            except Exception as e:
                logger.error(f"Error obteniendo odds de {league}: {e}")
                continue

        logger.warning(f"No se encontraron odds para {home_team} vs {away_team} en ninguna liga")
        return None

    def clear_cache(self):
        """Limpiar toda la caché"""
        self._cache.clear()
        logger.info("Cache cleared")


if __name__ == '__main__':
    """Test de todas las funciones con Premier League"""

    print("=" * 60)
    print("TEST: DataFetcher con football-data.org")
    print("=" * 60)

    try:
        fetcher = DataFetcher()

        # 1. Get competitions
        print("\n1. GET COMPETITIONS")
        print("-" * 60)
        competitions = fetcher.get_competitions()
        for comp in competitions[:5]:
            print(f"  {comp['code']:>6} | {comp['id']:>6} | {comp['name']} ({comp['area']})")

        # 2. Get team_id (Premier League = 2021)
        print("\n2. GET TEAM ID - Arsenal en Premier League")
        print("-" * 60)
        team_id = fetcher.get_team_id("Arsenal", 2021)
        print(f"  Arsenal ID: {team_id}")

        # 3. Get team stats
        if team_id:
            print("\n3. GET TEAM STATS - Arsenal")
            print("-" * 60)
            stats = fetcher.get_team_stats(team_id)
            print(f"  Attack:  {stats['attack']}/100")
            print(f"  Defense: {stats['defense']}/100")
            print(f"  Form:    {stats['form']}/100")
            if 'wins' in stats:
                print(f"  Record:  {stats['wins']}W-{stats['draws']}D-{stats['losses']}L")
                print(f"  Goles:   {stats['goals_for']} a favor, {stats['goals_against']} en contra")
            print(f"  Partidos analizados: {stats['total_matches']}")
            if stats['recent_matches']:
                print(f"  Últimos resultados:")
                for match in stats['recent_matches'][:5]:
                    home_str = "H" if match['home'] else "A"
                    print(f"    [{home_str}] vs {match['opponent']:20} | {match['result']} {match['score']}")
            else:
                print(f"  No hay partidos recientes disponibles")

        # 4. Get upcoming matches
        print("\n4. GET UPCOMING MATCHES - Premier League (próximos 7 días)")
        print("-" * 60)
        upcoming = fetcher.get_upcoming_matches(2021, days_ahead=7)
        for match in upcoming[:5]:
            date = datetime.fromisoformat(match['date'])
            print(f"  {date.strftime('%Y-%m-%d %H:%M')} | {match['home_team']} vs {match['away_team']}")

        # 5. Get match result (último partido encontrado)
        if upcoming:
            print("\n5. GET MATCH RESULT - Primer partido encontrado")
            print("-" * 60)
            first_match_id = upcoming[0]['match_id']
            result = fetcher.get_match_result(first_match_id)
            if result:
                print(f"  Partido: {result['home_team']} vs {result['away_team']}")
                print(f"  Status:  {result['status']}")
                if result['home_goals'] is not None:
                    print(f"  Score:   {result['home_goals']}-{result['away_goals']}")
                else:
                    print(f"  Score:   Aún no jugado")

        # 6. Get real odds
        print("\n6. GET REAL ODDS - Arsenal vs Liverpool")
        print("-" * 60)
        odds = fetcher.get_real_odds("Arsenal", "Liverpool")
        if odds:
            print(f"  HOME: {odds['home_win']}")
            print(f"  DRAW: {odds['draw']}")
            print(f"  AWAY: {odds['away_win']}")
            print(f"  Bookmaker: {odds['bookmaker']}")
            print(f"  Requests remaining: {odds['requests_remaining']}")
        else:
            print("  No se encontraron odds (fuera de temporada o sin partidos próximos)")

        print("\n" + "=" * 60)
        print("TEST COMPLETADO - OK")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
