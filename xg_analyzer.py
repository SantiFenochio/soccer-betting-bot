"""
xG (Expected Goals) Analyzer
Análisis avanzado usando Expected Goals de múltiples fuentes
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)


class xGAnalyzer:
    """Analizador de Expected Goals (xG)"""

    def __init__(self):
        """Inicializar analizador xG"""
        self.understat = None
        self.fbref = None
        self._init_data_sources()

    def _init_data_sources(self):
        """Inicializar fuentes de datos xG"""
        try:
            import soccerdata as sd

            # Understat - La mejor fuente de xG
            understat_leagues = ['La Liga', 'EPL', 'Bundesliga', 'Serie A', 'Ligue 1']
            self.understat = sd.Understat(leagues=understat_leagues)
            logger.info("✓ Understat inicializado para xG")

            # FBref como backup
            fbref_leagues = ['ENG-Premier League', 'ESP-La Liga', 'GER-Bundesliga',
                           'ITA-Serie A', 'FRA-Ligue 1']
            self.fbref = sd.FBref(leagues=fbref_leagues)
            logger.info("✓ FBref inicializado como backup")

        except Exception as e:
            logger.error(f"Error inicializando fuentes xG: {e}")

    def get_team_xg_stats(self, team_name: str, league: str = 'EPL', n_matches: int = 10) -> Dict:
        """
        Obtener estadísticas xG de un equipo

        Args:
            team_name: Nombre del equipo
            league: Liga (EPL, La Liga, etc.)
            n_matches: Número de partidos a analizar

        Returns:
            Dict con estadísticas xG
        """
        try:
            # Mapeo de ligas
            league_map = {
                'ENG': 'EPL',
                'ESP': 'La Liga',
                'GER': 'Bundesliga',
                'ITA': 'Serie A',
                'FRA': 'Ligue 1'
            }

            understat_league = league_map.get(league, league)

            # Obtener datos de Understat
            season = self._get_current_season()
            team_data = self.understat.read_team_match_stats(
                team=team_name,
                league=understat_league,
                season=season
            )

            if team_data.empty:
                logger.warning(f"No hay datos xG para {team_name}")
                return {'error': 'No xG data available'}

            # Ordenar por fecha (más recientes primero)
            team_data = team_data.sort_values('date', ascending=False).head(n_matches)

            # Calcular estadísticas xG
            stats = {
                'team': team_name,
                'league': league,
                'matches_analyzed': len(team_data),

                # xG Ofensivo
                'xg_for_avg': round(team_data['xG'].mean(), 2),
                'xg_for_total': round(team_data['xG'].sum(), 2),

                # xG Defensivo
                'xg_against_avg': round(team_data['xGA'].mean(), 2),
                'xg_against_total': round(team_data['xGA'].sum(), 2),

                # Goles reales
                'goals_scored_avg': round(team_data['scored'].mean(), 2),
                'goals_conceded_avg': round(team_data['missed'].mean(), 2),

                # Análisis de performance (over/under performance)
                'xg_overperformance': round(
                    team_data['scored'].sum() - team_data['xG'].sum(), 2
                ),
                'xg_defensive_overperformance': round(
                    team_data['xGA'].sum() - team_data['missed'].sum(), 2
                ),

                # Ratios importantes
                'xg_conversion_rate': round(
                    (team_data['scored'].sum() / team_data['xG'].sum() * 100)
                    if team_data['xG'].sum() > 0 else 0, 1
                ),

                # Tendencias
                'high_xg_matches': int((team_data['xG'] > 1.5).sum()),
                'low_xg_against_matches': int((team_data['xGA'] < 1.0).sum()),

                # Últimos 5 partidos
                'last_5_xg_avg': round(team_data.head(5)['xG'].mean(), 2),
                'last_5_xga_avg': round(team_data.head(5)['xGA'].mean(), 2),
            }

            # Añadir interpretación
            stats['interpretation'] = self._interpret_xg_stats(stats)

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo xG stats: {e}")
            return {'error': str(e)}

    def compare_teams_xg(self, home_team: str, away_team: str, league: str = 'EPL') -> Dict:
        """
        Comparar xG de dos equipos para un partido

        Args:
            home_team: Equipo local
            away_team: Equipo visitante
            league: Liga

        Returns:
            Comparación detallada con predicción
        """
        try:
            home_stats = self.get_team_xg_stats(home_team, league, n_matches=10)
            away_stats = self.get_team_xg_stats(away_team, league, n_matches=10)

            if 'error' in home_stats or 'error' in away_stats:
                return {'error': 'No se pudieron obtener datos xG para ambos equipos'}

            # Calcular predicción xG del partido
            home_xg_expected = (home_stats['xg_for_avg'] + away_stats['xg_against_avg']) / 2
            away_xg_expected = (away_stats['xg_for_avg'] + home_stats['xg_against_avg']) / 2

            # Ajustar por ventaja de local (típicamente +0.3 xG)
            home_xg_expected += 0.3

            total_xg_expected = home_xg_expected + away_xg_expected

            comparison = {
                'home_team': home_team,
                'away_team': away_team,
                'home_stats': home_stats,
                'away_stats': away_stats,

                # Predicción del partido
                'match_prediction': {
                    'home_xg_expected': round(home_xg_expected, 2),
                    'away_xg_expected': round(away_xg_expected, 2),
                    'total_xg_expected': round(total_xg_expected, 2),
                },

                # Análisis comparativo
                'analysis': {
                    'attacking_advantage': 'home' if home_stats['xg_for_avg'] > away_stats['xg_for_avg'] else 'away',
                    'defensive_advantage': 'home' if home_stats['xg_against_avg'] < away_stats['xg_against_avg'] else 'away',
                    'xg_difference': round(abs(home_stats['xg_for_avg'] - away_stats['xg_for_avg']), 2),
                },

                # Recomendaciones basadas en xG
                'recommendations': self._generate_xg_recommendations(
                    home_xg_expected, away_xg_expected, total_xg_expected,
                    home_stats, away_stats
                )
            }

            return comparison

        except Exception as e:
            logger.error(f"Error comparando equipos xG: {e}")
            return {'error': str(e)}

    def _generate_xg_recommendations(self, home_xg: float, away_xg: float,
                                    total_xg: float, home_stats: Dict,
                                    away_stats: Dict) -> List[Dict]:
        """Generar recomendaciones basadas en análisis xG"""
        recommendations = []

        # 1. TOTAL DE GOLES (Over/Under)
        if total_xg > 2.7:
            confidence = min(70 + int((total_xg - 2.7) * 20), 92)
            recommendations.append({
                'type': 'Goles - Over 2.5',
                'prediction': f'Over 2.5 goles',
                'confidence': confidence,
                'reasoning': f'xG total esperado: {total_xg:.2f}. Ambos equipos generan buenas oportunidades.',
                'xg_based': True
            })
        elif total_xg < 2.2:
            confidence = min(70 + int((2.2 - total_xg) * 20), 90)
            recommendations.append({
                'type': 'Goles - Under 2.5',
                'prediction': f'Under 2.5 goles',
                'confidence': confidence,
                'reasoning': f'xG total esperado: {total_xg:.2f}. Partido cerrado con pocas oportunidades.',
                'xg_based': True
            })

        # 2. RESULTADO
        xg_diff = home_xg - away_xg
        if abs(xg_diff) > 0.5:
            winner = 'Local' if xg_diff > 0 else 'Visitante'
            confidence = min(65 + int(abs(xg_diff) * 15), 85)
            recommendations.append({
                'type': 'Resultado',
                'prediction': f'Victoria {winner}',
                'confidence': confidence,
                'reasoning': f'Ventaja en xG: {abs(xg_diff):.2f}. Diferencia significativa en calidad de juego.',
                'xg_based': True
            })

        # 3. AMBOS ANOTAN (BTTS)
        if home_xg > 1.0 and away_xg > 1.0:
            confidence = min(65 + int((home_xg + away_xg - 2.0) * 10), 85)
            recommendations.append({
                'type': 'Ambos Anotan',
                'prediction': 'Sí (BTTS)',
                'confidence': confidence,
                'reasoning': f'Ambos equipos generan >1.0 xG. Local: {home_xg:.2f}, Visitante: {away_xg:.2f}',
                'xg_based': True
            })

        # 4. ANÁLISIS DE OVERPERFORMANCE
        home_overperf = home_stats.get('xg_overperformance', 0)
        away_overperf = away_stats.get('xg_overperformance', 0)

        if abs(home_overperf) > 3 or abs(away_overperf) > 3:
            team = home_stats['team'] if abs(home_overperf) > abs(away_overperf) else away_stats['team']
            value = home_overperf if abs(home_overperf) > abs(away_overperf) else away_overperf

            if value > 3:
                msg = f'{team} está sobre-performando (+{value:.1f} goles vs xG). Probable regresión a la media.'
            else:
                msg = f'{team} está bajo-performando ({value:.1f} goles vs xG). Probable mejora en resultados.'

            recommendations.append({
                'type': 'Análisis Avanzado',
                'prediction': 'Regresión a la media',
                'confidence': 70,
                'reasoning': msg,
                'xg_based': True
            })

        # 5. FORMA RECIENTE (últimos 5 vs promedio general)
        if home_stats['last_5_xg_avg'] > home_stats['xg_for_avg'] + 0.3:
            recommendations.append({
                'type': 'Forma',
                'prediction': f"{home_stats['team']} en racha ofensiva",
                'confidence': 72,
                'reasoning': f"xG últimos 5: {home_stats['last_5_xg_avg']:.2f} vs promedio: {home_stats['xg_for_avg']:.2f}",
                'xg_based': True
            })

        return recommendations

    def _interpret_xg_stats(self, stats: Dict) -> Dict:
        """Interpretar estadísticas xG para insights"""
        interpretation = {}

        # Calidad ofensiva
        xg_for = stats['xg_for_avg']
        if xg_for > 2.0:
            interpretation['attack'] = 'Excelente - Genera muchas oportunidades'
        elif xg_for > 1.5:
            interpretation['attack'] = 'Bueno - Ataque consistente'
        elif xg_for > 1.0:
            interpretation['attack'] = 'Promedio - Ataque moderado'
        else:
            interpretation['attack'] = 'Débil - Pocas oportunidades claras'

        # Calidad defensiva
        xg_against = stats['xg_against_avg']
        if xg_against < 0.8:
            interpretation['defense'] = 'Excelente - Muy sólidos atrás'
        elif xg_against < 1.2:
            interpretation['defense'] = 'Bueno - Defensa confiable'
        elif xg_against < 1.8:
            interpretation['defense'] = 'Promedio - Vulnerables ocasionalmente'
        else:
            interpretation['defense'] = 'Débil - Conceden muchas oportunidades'

        # Eficiencia (conversión)
        conversion = stats['xg_conversion_rate']
        if conversion > 110:
            interpretation['efficiency'] = 'Sobre-performando (regresión probable)'
        elif conversion > 90:
            interpretation['efficiency'] = 'Normal - Convirtiendo según lo esperado'
        else:
            interpretation['efficiency'] = 'Bajo-performando (mejora probable)'

        # Overperformance
        overperf = stats['xg_overperformance']
        if abs(overperf) < 2:
            interpretation['consistency'] = 'Resultados consistentes con rendimiento'
        elif overperf > 2:
            interpretation['consistency'] = f'Sobrepasando xG (+{overperf:.1f}) - Suerte/Calidad finishing'
        else:
            interpretation['consistency'] = f'Por debajo de xG ({overperf:.1f}) - Mala suerte/Bajo finishing'

        return interpretation

    def _get_current_season(self) -> str:
        """Obtener temporada actual en formato correcto"""
        now = datetime.now()
        year = now.year

        # Las temporadas europeas empiezan en agosto/septiembre
        if now.month >= 8:
            return f"{year}"
        else:
            return f"{year - 1}"

    def format_xg_analysis_for_telegram(self, comparison: Dict) -> str:
        """
        Formatear análisis xG para mostrar en Telegram

        Args:
            comparison: Diccionario con comparación xG

        Returns:
            String formateado para Telegram
        """
        if 'error' in comparison:
            return f"⚠️ {comparison['error']}"

        home = comparison['home_team']
        away = comparison['away_team']
        pred = comparison['match_prediction']
        home_stats = comparison['home_stats']
        away_stats = comparison['away_stats']

        msg = f"📊 *ANÁLISIS xG (Expected Goals)*\n\n"

        # Predicción del partido
        msg += f"🎯 *Predicción xG del Partido:*\n"
        msg += f"🏠 {home}: {pred['home_xg_expected']} xG\n"
        msg += f"🚗 {away}: {pred['away_xg_expected']} xG\n"
        msg += f"⚽ Total esperado: {pred['total_xg_expected']} goles\n\n"

        # Stats de cada equipo
        msg += f"📈 *Estadísticas Últimos 10 Partidos:*\n\n"

        msg += f"🏠 *{home}:*\n"
        msg += f"   ⚔️ xG Ofensivo: {home_stats['xg_for_avg']}/partido\n"
        msg += f"   🛡️ xG Defensivo: {home_stats['xg_against_avg']}/partido\n"
        msg += f"   🎯 Conversión: {home_stats['xg_conversion_rate']}%\n"
        msg += f"   📊 {home_stats['interpretation']['attack']}\n"
        msg += f"   📊 {home_stats['interpretation']['defense']}\n\n"

        msg += f"🚗 *{away}:*\n"
        msg += f"   ⚔️ xG Ofensivo: {away_stats['xg_for_avg']}/partido\n"
        msg += f"   🛡️ xG Defensivo: {away_stats['xg_against_avg']}/partido\n"
        msg += f"   🎯 Conversión: {away_stats['xg_conversion_rate']}%\n"
        msg += f"   📊 {away_stats['interpretation']['attack']}\n"
        msg += f"   📊 {away_stats['interpretation']['defense']}\n\n"

        # Recomendaciones basadas en xG
        if comparison['recommendations']:
            msg += f"💡 *RECOMENDACIONES BASADAS EN xG:*\n\n"

            for i, rec in enumerate(comparison['recommendations'][:4], 1):
                conf = rec['confidence']
                emoji = "🔥🔥" if conf >= 80 else "🔥" if conf >= 70 else "✅"

                msg += f"*{i}. {rec['type']}* {emoji}\n"
                msg += f"   🎲 {rec['prediction']}\n"
                msg += f"   📈 Confianza: {conf}%\n"
                msg += f"   ℹ️ {rec['reasoning']}\n\n"

        msg += "\n📚 _xG = Expected Goals (goles esperados según calidad de oportunidades)_"

        return msg


if __name__ == '__main__':
    # Test del analizador xG
    print("🧪 Testing xG Analyzer...\n")

    analyzer = xGAnalyzer()

    # Test: Liverpool vs Arsenal
    print("=" * 60)
    print("Comparación xG: Manchester City vs Liverpool")
    print("=" * 60)

    comparison = analyzer.compare_teams_xg('Manchester City', 'Liverpool', 'EPL')

    if 'error' not in comparison:
        formatted = analyzer.format_xg_analysis_for_telegram(comparison)
        print(formatted)
    else:
        print(f"Error: {comparison['error']}")
