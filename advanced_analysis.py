"""
Advanced Analysis Module
Módulo de análisis avanzado: Head-to-Head, Momentum, Form
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)


class AdvancedAnalyzer:
    """Analizador avanzado para H2H y momentum"""

    def __init__(self):
        """Inicializar analizador avanzado"""
        self.fbref = None
        self.understat = None
        self._init_data_sources()

    def _init_data_sources(self):
        """Inicializar fuentes de datos"""
        try:
            import soccerdata as sd

            fbref_leagues = ['ENG-Premier League', 'ESP-La Liga', 'GER-Bundesliga',
                           'ITA-Serie A', 'FRA-Ligue 1']
            self.fbref = sd.FBref(leagues=fbref_leagues)

            understat_leagues = ['EPL', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']
            self.understat = sd.Understat(leagues=understat_leagues)

            logger.info("✓ Fuentes de datos inicializadas para análisis avanzado")

        except Exception as e:
            logger.error(f"Error inicializando fuentes: {e}")

    def analyze_head_to_head(self, home_team: str, away_team: str,
                            league: str = 'ENG', n_matches: int = 5) -> Dict:
        """
        Analizar últimos enfrentamientos directos (H2H)

        Args:
            home_team: Equipo local
            away_team: Equipo visitante
            league: Liga
            n_matches: Número de enfrentamientos a analizar

        Returns:
            Análisis H2H completo
        """
        try:
            # Mapeo de ligas
            league_map = {
                'ENG': 'ENG-Premier League',
                'ESP': 'ESP-La Liga',
                'GER': 'GER-Bundesliga',
                'ITA': 'ITA-Serie A',
                'FRA': 'FRA-Ligue 1'
            }

            fbref_league = league_map.get(league, 'ENG-Premier League')

            # Obtener resultados de la temporada actual y anterior
            current_season = self._get_current_season()
            prev_season = self._get_previous_season()

            h2h_matches = []

            for season in [current_season, prev_season]:
                try:
                    schedule = self.fbref.read_schedule(league, season)

                    # Filtrar enfrentamientos entre estos equipos
                    h2h = schedule[
                        ((schedule['Home'] == home_team) & (schedule['Away'] == away_team)) |
                        ((schedule['Home'] == away_team) & (schedule['Away'] == home_team))
                    ]

                    if not h2h.empty:
                        h2h_matches.append(h2h)

                except Exception as e:
                    logger.warning(f"No se pudo obtener schedule para {season}: {e}")
                    continue

            if not h2h_matches:
                return {'error': 'No se encontraron enfrentamientos previos'}

            # Combinar todos los enfrentamientos
            all_h2h = pd.concat(h2h_matches).sort_values('Date', ascending=False).head(n_matches)

            # Analizar resultados
            analysis = self._analyze_h2h_results(all_h2h, home_team, away_team)

            return analysis

        except Exception as e:
            logger.error(f"Error en análisis H2H: {e}")
            return {'error': str(e)}

    def _analyze_h2h_results(self, h2h_df: pd.DataFrame, home_team: str, away_team: str) -> Dict:
        """Analizar resultados de H2H"""
        if h2h_df.empty:
            return {'error': 'Sin datos H2H'}

        total_matches = len(h2h_df)
        home_wins = 0
        away_wins = 0
        draws = 0
        total_goals = 0
        home_goals = 0
        away_goals = 0
        over_25 = 0
        btts = 0

        for _, match in h2h_df.iterrows():
            home = match.get('Home')
            away = match.get('Away')
            score = match.get('Score')

            if not score or '-' not in str(score):
                continue

            try:
                goals_home, goals_away = map(int, str(score).split('-'))
                total_goals += goals_home + goals_away

                # Determinar quién jugó de local en este partido histórico
                if home == home_team:
                    home_goals += goals_home
                    away_goals += goals_away

                    if goals_home > goals_away:
                        home_wins += 1
                    elif goals_away > goals_home:
                        away_wins += 1
                    else:
                        draws += 1
                else:
                    home_goals += goals_away
                    away_goals += goals_home

                    if goals_away > goals_home:
                        home_wins += 1
                    elif goals_home > goals_away:
                        away_wins += 1
                    else:
                        draws += 1

                # Over 2.5
                if (goals_home + goals_away) > 2.5:
                    over_25 += 1

                # BTTS
                if goals_home > 0 and goals_away > 0:
                    btts += 1

            except:
                continue

        avg_goals = total_goals / total_matches if total_matches > 0 else 0
        over_25_pct = (over_25 / total_matches * 100) if total_matches > 0 else 0
        btts_pct = (btts / total_matches * 100) if total_matches > 0 else 0

        return {
            'home_team': home_team,
            'away_team': away_team,
            'matches_analyzed': total_matches,
            'results': {
                f'{home_team}_wins': home_wins,
                f'{away_team}_wins': away_wins,
                'draws': draws
            },
            'goals': {
                'total': total_goals,
                'average': round(avg_goals, 2),
                f'{home_team}_scored': home_goals,
                f'{away_team}_scored': away_goals,
                f'{home_team}_avg': round(home_goals / total_matches, 2) if total_matches > 0 else 0,
                f'{away_team}_avg': round(away_goals / total_matches, 2) if total_matches > 0 else 0
            },
            'trends': {
                'over_25_count': over_25,
                'over_25_percentage': round(over_25_pct, 1),
                'btts_count': btts,
                'btts_percentage': round(btts_pct, 1)
            },
            'recommendations': self._generate_h2h_recommendations(
                home_wins, away_wins, draws, over_25_pct, btts_pct, avg_goals
            )
        }

    def analyze_momentum(self, team_name: str, league: str = 'ENG', n_matches: int = 5) -> Dict:
        """
        Analizar momentum/racha actual de un equipo

        Args:
            team_name: Nombre del equipo
            league: Liga
            n_matches: Número de partidos recientes a analizar

        Returns:
            Análisis de momentum
        """
        try:
            # Mapeo de ligas
            league_map = {
                'ENG': 'ENG-Premier League',
                'ESP': 'ESP-La Liga',
                'GER': 'GER-Bundesliga',
                'ITA': 'ITA-Serie A',
                'FRA': 'FRA-Ligue 1'
            }

            fbref_league = league_map.get(league, 'ENG-Premier League')
            season = self._get_current_season()

            # Obtener schedule
            schedule = self.fbref.read_schedule(league, season)

            # Filtrar partidos del equipo
            team_matches = schedule[
                (schedule['Home'] == team_name) | (schedule['Away'] == team_name)
            ].sort_values('Date', ascending=False).head(n_matches)

            if team_matches.empty:
                return {'error': f'No se encontraron partidos para {team_name}'}

            # Analizar momentum
            analysis = self._analyze_team_momentum(team_matches, team_name)

            return analysis

        except Exception as e:
            logger.error(f"Error analizando momentum: {e}")
            return {'error': str(e)}

    def _analyze_team_momentum(self, matches_df: pd.DataFrame, team_name: str) -> Dict:
        """Analizar momentum del equipo"""
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        points = 0
        results = []
        clean_sheets = 0

        for _, match in matches_df.iterrows():
            home = match.get('Home')
            away = match.get('Away')
            score = match.get('Score')

            if not score or '-' not in str(score):
                continue

            try:
                goals_home, goals_away = map(int, str(score).split('-'))

                # Determinar resultado desde perspectiva del equipo
                if home == team_name:
                    goals_scored += goals_home
                    goals_conceded += goals_away

                    if goals_home > goals_away:
                        wins += 1
                        points += 3
                        results.append('W')
                    elif goals_home == goals_away:
                        draws += 1
                        points += 1
                        results.append('D')
                    else:
                        losses += 1
                        results.append('L')

                    if goals_away == 0:
                        clean_sheets += 1

                else:  # Away
                    goals_scored += goals_away
                    goals_conceded += goals_home

                    if goals_away > goals_home:
                        wins += 1
                        points += 3
                        results.append('W')
                    elif goals_away == goals_home:
                        draws += 1
                        points += 1
                        results.append('D')
                    else:
                        losses += 1
                        results.append('L')

                    if goals_home == 0:
                        clean_sheets += 1

            except:
                continue

        total_matches = len(matches_df)

        # Calcular racha
        streak = self._calculate_momentum_streak(results)

        # Forma (puntos promedio)
        points_per_game = points / total_matches if total_matches > 0 else 0

        # Clasificar momentum
        if points_per_game >= 2.5:
            momentum_rating = "🔥🔥🔥 EXCELENTE"
        elif points_per_game >= 2.0:
            momentum_rating = "🔥🔥 MUY BUENO"
        elif points_per_game >= 1.5:
            momentum_rating = "🔥 BUENO"
        elif points_per_game >= 1.0:
            momentum_rating = "⚡ REGULAR"
        else:
            momentum_rating = "❄️ MALO"

        return {
            'team': team_name,
            'matches_analyzed': total_matches,
            'results': {
                'wins': wins,
                'draws': draws,
                'losses': losses,
                'results_sequence': results  # ['W', 'W', 'D', 'L', 'W']
            },
            'performance': {
                'points': points,
                'points_per_game': round(points_per_game, 2),
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded,
                'goal_difference': goals_scored - goals_conceded,
                'goals_per_game': round(goals_scored / total_matches, 2) if total_matches > 0 else 0,
                'clean_sheets': clean_sheets
            },
            'streak': streak,
            'momentum_rating': momentum_rating,
            'recommendations': self._generate_momentum_recommendations(
                points_per_game, streak, goals_scored / total_matches if total_matches > 0 else 0
            )
        }

    def _calculate_momentum_streak(self, results: List[str]) -> Dict:
        """Calcular racha actual"""
        if not results:
            return {'type': 'none', 'count': 0}

        current = results[0]
        count = 1

        for result in results[1:]:
            if result == current:
                count += 1
            else:
                break

        streak_type = {
            'W': 'winning',
            'D': 'drawing',
            'L': 'losing'
        }.get(current, 'none')

        return {
            'type': streak_type,
            'count': count,
            'current_result': current
        }

    def _generate_h2h_recommendations(self, home_wins: int, away_wins: int,
                                     draws: int, over_25_pct: float,
                                     btts_pct: float, avg_goals: float) -> List[str]:
        """Generar recomendaciones basadas en H2H"""
        recommendations = []

        total = home_wins + away_wins + draws

        if total > 0:
            home_win_pct = (home_wins / total * 100)
            away_win_pct = (away_wins / total * 100)

            if home_win_pct > 60:
                recommendations.append(f"🏠 Victoria local muy probable ({home_win_pct:.0f}% histórico)")
            elif away_win_pct > 60:
                recommendations.append(f"🚗 Victoria visitante muy probable ({away_win_pct:.0f}% histórico)")
            elif (draws / total * 100) > 40:
                recommendations.append(f"➖ Empate común en este enfrentamiento")

        if over_25_pct > 70:
            recommendations.append(f"⚽ Over 2.5 goles muy probable ({over_25_pct:.0f}% histórico)")
        elif over_25_pct < 30:
            recommendations.append(f"🔒 Under 2.5 goles probable ({100-over_25_pct:.0f}% histórico)")

        if btts_pct > 70:
            recommendations.append(f"🎯 BTTS muy probable ({btts_pct:.0f}% histórico)")

        if avg_goals > 3.5:
            recommendations.append(f"🔥 Partidos históricamente ofensivos (prom: {avg_goals:.1f} goles)")

        return recommendations

    def _generate_momentum_recommendations(self, ppg: float, streak: Dict, gpg: float) -> List[str]:
        """Generar recomendaciones basadas en momentum"""
        recommendations = []

        if ppg >= 2.5:
            recommendations.append("🔥 Equipo en forma excepcional")
        elif ppg >= 2.0:
            recommendations.append("✅ Equipo en buena forma")
        elif ppg < 1.0:
            recommendations.append("⚠️ Equipo en mala racha")

        if streak['type'] == 'winning' and streak['count'] >= 3:
            recommendations.append(f"🔥 Racha de {streak['count']} victorias consecutivas")
        elif streak['type'] == 'losing' and streak['count'] >= 3:
            recommendations.append(f"❄️ Racha de {streak['count']} derrotas consecutivas")

        if gpg > 2.0:
            recommendations.append(f"⚽ Ataque en llamas ({gpg:.1f} goles/partido)")
        elif gpg < 0.8:
            recommendations.append(f"🔒 Problemas ofensivos ({gpg:.1f} goles/partido)")

        return recommendations

    def _get_current_season(self) -> str:
        """Obtener temporada actual"""
        now = datetime.now()
        year = now.year

        if now.month >= 8:
            return f"{year}"
        else:
            return f"{year - 1}"

    def _get_previous_season(self) -> str:
        """Obtener temporada anterior"""
        current = int(self._get_current_season())
        return f"{current - 1}"

    def format_h2h_for_telegram(self, analysis: Dict) -> str:
        """Formatear H2H para Telegram"""
        if 'error' in analysis:
            return f"⚠️ {analysis['error']}"

        home = analysis['home_team']
        away = analysis['away_team']
        results = analysis['results']
        goals = analysis['goals']
        trends = analysis['trends']

        msg = f"⚔️ *HEAD-TO-HEAD: Últimos {analysis['matches_analyzed']} enfrentamientos*\n\n"

        msg += f"🏆 *Resultados:*\n"
        msg += f"   🏠 {home}: {results[f'{home}_wins']} victorias\n"
        msg += f"   🚗 {away}: {results[f'{away}_wins']} victorias\n"
        msg += f"   ➖ Empates: {results['draws']}\n\n"

        msg += f"⚽ *Goles:*\n"
        msg += f"   📊 Promedio total: {goals['average']} goles/partido\n"
        msg += f"   🏠 {home}: {goals[f'{home}_avg']} goles/partido\n"
        msg += f"   🚗 {away}: {goals[f'{away}_avg']} goles/partido\n\n"

        msg += f"📈 *Tendencias:*\n"
        msg += f"   🔺 Over 2.5: {trends['over_25_count']}/{analysis['matches_analyzed']} ({trends['over_25_percentage']}%)\n"
        msg += f"   🎯 BTTS: {trends['btts_count']}/{analysis['matches_analyzed']} ({trends['btts_percentage']}%)\n\n"

        if analysis['recommendations']:
            msg += f"💡 *Conclusiones:*\n"
            for rec in analysis['recommendations']:
                msg += f"   • {rec}\n"

        return msg

    def format_momentum_for_telegram(self, analysis: Dict) -> str:
        """Formatear momentum para Telegram"""
        if 'error' in analysis:
            return f"⚠️ {analysis['error']}"

        team = analysis['team']
        results = analysis['results']
        perf = analysis['performance']
        streak = analysis['streak']

        msg = f"📊 *MOMENTUM: {team}*\n"
        msg += f"_{analysis['momentum_rating']}_\n\n"

        msg += f"📈 *Últimos {analysis['matches_analyzed']} partidos:*\n"
        msg += f"   ✅ {results['wins']}W  ➖ {results['draws']}D  ❌ {results['losses']}L\n"
        msg += f"   Forma: {' '.join(results['results_sequence'])}\n\n"

        msg += f"🎯 *Rendimiento:*\n"
        msg += f"   📊 Puntos/partido: {perf['points_per_game']}\n"
        msg += f"   ⚽ Goles: {perf['goals_scored']} ({perf['goals_per_game']}/partido)\n"
        msg += f"   🛡️ Goles recibidos: {perf['goals_conceded']}\n"
        msg += f"   📈 Diferencia: {perf['goal_difference']:+d}\n"
        msg += f"   🧤 Vallas invictas: {perf['clean_sheets']}\n\n"

        if streak['count'] > 0:
            streak_emoji = {"winning": "🔥", "drawing": "➖", "losing": "❄️"}.get(streak['type'], "")
            streak_text = {"winning": "victorias", "drawing": "empates", "losing": "derrotas"}.get(streak['type'], "")
            msg += f"{streak_emoji} *Racha:* {streak['count']} {streak_text} consecutivas\n\n"

        if analysis['recommendations']:
            msg += f"💡 *Análisis:*\n"
            for rec in analysis['recommendations']:
                msg += f"   • {rec}\n"

        return msg


if __name__ == '__main__':
    # Test del analizador avanzado
    print("🧪 Testing Advanced Analyzer...\n")

    analyzer = AdvancedAnalyzer()

    # Test H2H
    print("=" * 60)
    print("Test: Head-to-Head Analysis")
    print("=" * 60)

    h2h = analyzer.analyze_head_to_head('Manchester City', 'Liverpool', 'ENG', n_matches=5)

    if 'error' not in h2h:
        formatted = analyzer.format_h2h_for_telegram(h2h)
        print(formatted)
    else:
        print(f"Error: {h2h['error']}")

    # Test Momentum
    print("\n" + "=" * 60)
    print("Test: Momentum Analysis")
    print("=" * 60)

    momentum = analyzer.analyze_momentum('Manchester City', 'ENG', n_matches=5)

    if 'error' not in momentum:
        formatted = analyzer.format_momentum_for_telegram(momentum)
        print(formatted)
    else:
        print(f"Error: {momentum['error']}")
