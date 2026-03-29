"""
Daily Locks Analyzer
Sistema profesional para encontrar las 3 mejores apuestas del día
Basado en metodologías de BetQL, Covers y análisis profesional
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class DailyLocksAnalyzer:
    """Analizador de 'locks' o apuestas más seguras del día"""

    def __init__(self):
        """Inicializar analizador de locks"""
        self.xg_analyzer = None
        self.advanced_analyzer = None
        self.value_analyzer = None
        self.prediction_engine = None
        self._init_analyzers()

    def _init_analyzers(self):
        """Inicializar todos los analizadores"""
        try:
            from xg_analyzer import xGAnalyzer
            self.xg_analyzer = xGAnalyzer()
            logger.info("✓ xG Analyzer cargado para locks")
        except Exception as e:
            logger.warning(f"xG Analyzer no disponible: {e}")

        try:
            from advanced_analysis import AdvancedAnalyzer
            self.advanced_analyzer = AdvancedAnalyzer()
            logger.info("✓ Advanced Analyzer cargado para locks")
        except Exception as e:
            logger.warning(f"Advanced Analyzer no disponible: {e}")

        try:
            from value_bets import ValueBetsAnalyzer
            self.value_analyzer = ValueBetsAnalyzer()
            logger.info("✓ Value Bets Analyzer cargado para locks")
        except Exception as e:
            logger.warning(f"Value Analyzer no disponible: {e}")

        try:
            from prediction_engine import PredictionEngine
            self.prediction_engine = PredictionEngine()
            logger.info("✓ Prediction Engine cargado para locks")
        except Exception as e:
            logger.warning(f"Prediction Engine no disponible: {e}")

    def find_daily_locks(self, matches: List[Dict], top_n: int = 3) -> List[Dict]:
        """
        Encontrar las mejores apuestas del día

        Args:
            matches: Lista de partidos del día
            top_n: Número de locks a retornar (default: 3)

        Returns:
            Lista de locks ordenados por confianza
        """
        if not matches:
            logger.warning("No hay partidos para analizar")
            return []

        logger.info(f"Analizando {len(matches)} partidos para encontrar locks...")

        all_bets = []

        # Analizar cada partido
        for match in matches[:50]:  # Limitar a 50 partidos para performance
            try:
                home = match.get('home', match.get('home_team', ''))
                away = match.get('away', match.get('away_team', ''))
                league = match.get('league', '')

                if not home or not away:
                    continue

                logger.info(f"Analizando: {home} vs {away}")

                # Obtener todas las predicciones para este partido
                match_bets = self._analyze_match_for_locks(match, home, away, league)

                all_bets.extend(match_bets)

            except Exception as e:
                logger.error(f"Error analizando partido: {e}")
                continue

        if not all_bets:
            logger.warning("No se encontraron bets para analizar")
            return []

        # Ordenar por score total (descendente)
        all_bets.sort(key=lambda x: x['total_score'], reverse=True)

        # Tomar top N
        locks = all_bets[:top_n]

        # Asignar ratings (estrellas)
        for i, lock in enumerate(locks, 1):
            lock['rank'] = i
            lock['rating'] = self._calculate_star_rating(lock['total_score'])

        logger.info(f"✓ {len(locks)} locks identificados")

        return locks

    def _analyze_match_for_locks(self, match: Dict, home: str, away: str, league: str) -> List[Dict]:
        """
        Analizar un partido específico para posibles locks

        Returns:
            Lista de posibles apuestas con scores
        """
        bets = []

        # 1. Obtener predicciones base
        predictions = match.get('predictions', [])

        if not predictions and self.prediction_engine:
            try:
                analysis = self.prediction_engine.analyze_match(home, away, league)
                predictions = analysis.get('predictions', [])
            except:
                predictions = []

        # 2. Para cada predicción, calcular score compuesto
        for pred in predictions:
            if pred.get('confidence', 0) < 60:  # Solo considerar >60% confianza
                continue

            try:
                bet_score = self._calculate_bet_score(
                    match, home, away, league, pred
                )

                if bet_score['total_score'] >= 70:  # Umbral mínimo
                    bets.append(bet_score)

            except Exception as e:
                logger.debug(f"Error calculando score: {e}")
                continue

        return bets

    def _calculate_bet_score(self, match: Dict, home: str, away: str,
                            league: str, prediction: Dict) -> Dict:
        """
        Calcular score compuesto para una apuesta

        Factores evaluados (basado en investigación):
        1. Confidence base (30 pts)
        2. Team form/momentum (20 pts)
        3. xG data (20 pts)
        4. H2H history (15 pts)
        5. Value/EV (15 pts)

        Returns:
            Dict con score y detalles
        """
        scores = {
            'confidence': 0,
            'form': 0,
            'xg': 0,
            'h2h': 0,
            'value': 0
        }

        factors_analyzed = []

        # 1. CONFIDENCE BASE (30 puntos)
        base_confidence = prediction.get('confidence', 0)
        scores['confidence'] = (base_confidence / 100) * 30
        factors_analyzed.append(f"Confianza base: {base_confidence}%")

        # 2. TEAM FORM/MOMENTUM (20 puntos)
        try:
            if self.advanced_analyzer:
                # Analizar momentum del favorito
                if 'victoria' in prediction.get('prediction', '').lower():
                    if home.lower() in prediction.get('prediction', '').lower():
                        team_to_check = home
                    else:
                        team_to_check = away

                    momentum = self.advanced_analyzer.analyze_momentum(team_to_check, league, n_matches=5)

                    if 'error' not in momentum:
                        ppg = momentum['performance']['points_per_game']

                        # Escalar PPG (0-3) a puntos (0-20)
                        if ppg >= 2.5:
                            scores['form'] = 20
                            factors_analyzed.append(f"Forma excepcional: {ppg} pts/partido")
                        elif ppg >= 2.0:
                            scores['form'] = 15
                            factors_analyzed.append(f"Buena forma: {ppg} pts/partido")
                        elif ppg >= 1.5:
                            scores['form'] = 10
                            factors_analyzed.append(f"Forma regular: {ppg} pts/partido")
                        else:
                            scores['form'] = 5
                            factors_analyzed.append(f"Forma baja: {ppg} pts/partido")
        except Exception as e:
            logger.debug(f"Error analizando form: {e}")
            scores['form'] = 10  # Neutral

        # 3. xG DATA (20 puntos)
        try:
            if self.xg_analyzer and league in ['ENG', 'ESP', 'GER', 'ITA', 'FRA']:
                xg_comparison = self.xg_analyzer.compare_teams_xg(home, away, league)

                if 'error' not in xg_comparison:
                    pred_type = prediction.get('type', '').lower()

                    if 'gol' in pred_type:
                        # Para predicciones de goles
                        total_xg = xg_comparison['match_prediction']['total_xg_expected']

                        if 'over' in prediction.get('prediction', '').lower():
                            if total_xg > 2.8:
                                scores['xg'] = 20
                                factors_analyzed.append(f"xG muy alto: {total_xg:.1f}")
                            elif total_xg > 2.5:
                                scores['xg'] = 15
                                factors_analyzed.append(f"xG favorable: {total_xg:.1f}")
                            else:
                                scores['xg'] = 8

                        elif 'under' in prediction.get('prediction', '').lower():
                            if total_xg < 2.0:
                                scores['xg'] = 20
                                factors_analyzed.append(f"xG bajo: {total_xg:.1f}")
                            elif total_xg < 2.3:
                                scores['xg'] = 15
                            else:
                                scores['xg'] = 8

                    # Para predicciones de resultado, ver diferencia xG
                    elif 'victoria' in pred_type or 'ganador' in pred_type:
                        home_xg = xg_comparison['match_prediction']['home_xg_expected']
                        away_xg = xg_comparison['match_prediction']['away_xg_expected']
                        diff = abs(home_xg - away_xg)

                        if diff > 0.8:
                            scores['xg'] = 20
                            factors_analyzed.append(f"Ventaja xG clara: {diff:.1f}")
                        elif diff > 0.5:
                            scores['xg'] = 15
                            factors_analyzed.append(f"Ventaja xG moderada: {diff:.1f}")
                        else:
                            scores['xg'] = 10

        except Exception as e:
            logger.debug(f"Error analizando xG: {e}")
            scores['xg'] = 10  # Neutral

        # 4. HEAD-TO-HEAD (15 puntos)
        try:
            if self.advanced_analyzer:
                h2h = self.advanced_analyzer.analyze_head_to_head(home, away, league, n_matches=5)

                if 'error' not in h2h:
                    pred_lower = prediction.get('prediction', '').lower()

                    # Para predicciones de goles
                    if 'over' in pred_lower:
                        over_pct = h2h['trends']['over_25_percentage']
                        if over_pct > 70:
                            scores['h2h'] = 15
                            factors_analyzed.append(f"H2H Over: {over_pct}%")
                        elif over_pct > 60:
                            scores['h2h'] = 10
                        else:
                            scores['h2h'] = 5

                    elif 'under' in pred_lower:
                        over_pct = h2h['trends']['over_25_percentage']
                        under_pct = 100 - over_pct
                        if under_pct > 70:
                            scores['h2h'] = 15
                            factors_analyzed.append(f"H2H Under: {under_pct}%")
                        elif under_pct > 60:
                            scores['h2h'] = 10
                        else:
                            scores['h2h'] = 5

                    # Para BTTS
                    elif 'btts' in pred_lower or 'ambos' in pred_lower:
                        btts_pct = h2h['trends']['btts_percentage']
                        if btts_pct > 70:
                            scores['h2h'] = 15
                            factors_analyzed.append(f"H2H BTTS: {btts_pct}%")
                        elif btts_pct > 60:
                            scores['h2h'] = 10
                        else:
                            scores['h2h'] = 5

        except Exception as e:
            logger.debug(f"Error analizando H2H: {e}")
            scores['h2h'] = 7  # Neutral

        # 5. VALUE/EV (15 puntos)
        # Si hay value bet detectado, bonus points
        if match.get('has_value_bets') and match.get('value_bets'):
            for vb in match['value_bets']:
                if vb.get('prediction', '').lower() in prediction.get('prediction', '').lower():
                    ev = vb['value_analysis']['expected_value']

                    if ev > 15:
                        scores['value'] = 15
                        factors_analyzed.append(f"Value excepcional: +{ev}%")
                    elif ev > 10:
                        scores['value'] = 12
                        factors_analyzed.append(f"Buen value: +{ev}%")
                    elif ev > 5:
                        scores['value'] = 8
                        factors_analyzed.append(f"Value detectado: +{ev}%")
                    break

        # CALCULAR SCORE TOTAL
        total_score = sum(scores.values())

        # Bonus: Si múltiples factores coinciden (consistencia)
        high_scores = sum(1 for score in scores.values() if score >= 15)
        if high_scores >= 3:
            total_score += 10  # Bonus de consistencia
            factors_analyzed.append("⭐ Bonus consistencia (3+ factores altos)")

        return {
            'match': f"{home} vs {away}",
            'home': home,
            'away': away,
            'league': league,
            'time': match.get('time', ''),
            'prediction_type': prediction.get('type', ''),
            'prediction': prediction.get('prediction', ''),
            'recommended_bet': prediction.get('recommended_bet', prediction.get('prediction', '')),
            'confidence': prediction.get('confidence', 0),
            'total_score': round(total_score, 1),
            'scores_breakdown': scores,
            'factors_analyzed': factors_analyzed,
            'reasoning': prediction.get('description', '')
        }

    def _calculate_star_rating(self, total_score: float) -> str:
        """
        Calcular rating de estrellas (1-5) basado en score total

        Sistema similar a BetQL y Covers
        """
        if total_score >= 90:
            return "⭐⭐⭐⭐⭐"  # 5 estrellas - Lock máximo
        elif total_score >= 80:
            return "⭐⭐⭐⭐"    # 4 estrellas - Muy confiable
        elif total_score >= 75:
            return "⭐⭐⭐"      # 3 estrellas - Confiable
        elif total_score >= 70:
            return "⭐⭐"        # 2 estrellas - Moderado
        else:
            return "⭐"          # 1 estrella - Bajo

    def format_locks_for_telegram(self, locks: List[Dict]) -> str:
        """
        Formatear locks para mostrar en Telegram

        Args:
            locks: Lista de locks encontrados

        Returns:
            String formateado para Telegram
        """
        if not locks:
            return (
                "🔍 *ANÁLISIS COMPLETO REALIZADO*\n\n"
                "No se encontraron apuestas con alta confianza hoy.\n\n"
                "💡 Esto significa:\n"
                "• Los partidos de hoy son muy inciertos\n"
                "• Las odds no ofrecen value suficiente\n"
                "• Mejor esperar a mejores oportunidades\n\n"
                "⚠️ No forzar apuestas sin confianza alta."
            )

        msg = "🔥 *FIJINI - TOP 3 LOCKS DEL DÍA* 🔥\n\n"
        msg += "_Las 3 mejores apuestas con mayor probabilidad de éxito_\n"
        msg += "_Análisis multi-factorial: xG + Form + H2H + Value_\n\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        for lock in locks:
            rank = lock['rank']
            rating = lock['rating']
            match = lock['match']
            league = lock['league']
            time = lock['time']
            bet = lock['recommended_bet']
            confidence = lock['confidence']
            total_score = lock['total_score']

            # Emoji según ranking
            rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, "🏅")

            msg += f"*{rank_emoji} LOCK #{rank}* {rating}\n"
            msg += f"━━━━━━━━━━━━━━━━━\n\n"

            msg += f"⚽ *Partido:* {match}\n"
            msg += f"🏆 *Liga:* {league}\n"

            # Formatear hora
            try:
                if 'T' in time:
                    from datetime import datetime
                    dt = datetime.fromisoformat(time.replace('Z', '+00:00'))
                    msg += f"🕐 *Hora:* {dt.strftime('%H:%M')}hs\n"
                else:
                    msg += f"🕐 *Hora:* {time}\n"
            except:
                msg += f"🕐 *Hora:* {time}\n"

            msg += f"\n🎯 *APUESTA RECOMENDADA:*\n"
            msg += f"   💡 {bet}\n"
            msg += f"   📊 Confianza: {confidence}%\n"
            msg += f"   🎲 Score Total: *{total_score}/100*\n\n"

            # Breakdown de scores
            msg += f"📈 *Análisis Multi-Factorial:*\n"
            breakdown = lock['scores_breakdown']
            msg += f"   • Base: {breakdown['confidence']:.0f}/30\n"
            msg += f"   • Forma: {breakdown['form']:.0f}/20\n"
            msg += f"   • xG: {breakdown['xg']:.0f}/20\n"
            msg += f"   • H2H: {breakdown['h2h']:.0f}/15\n"
            msg += f"   • Value: {breakdown['value']:.0f}/15\n\n"

            # Factores clave
            if lock['factors_analyzed']:
                msg += f"🔍 *Factores Clave:*\n"
                for factor in lock['factors_analyzed'][:3]:  # Top 3 factores
                    msg += f"   ✓ {factor}\n"
                msg += "\n"

            # Razonamiento
            if lock['reasoning']:
                msg += f"💭 _{lock['reasoning']}_\n"

            msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Footer con disclaimer
        msg += "📊 *METODOLOGÍA:*\n"
        msg += "Análisis basado en 5 factores:\n"
        msg += "• Confianza base del modelo\n"
        msg += "• Forma/momentum reciente\n"
        msg += "• Expected Goals (xG)\n"
        msg += "• Historial head-to-head\n"
        msg += "• Expected Value (EV)\n\n"

        msg += "⭐ *RATING:*\n"
        msg += "⭐⭐⭐⭐⭐ = Lock máximo (90+)\n"
        msg += "⭐⭐⭐⭐ = Muy confiable (80+)\n"
        msg += "⭐⭐⭐ = Confiable (75+)\n\n"

        msg += "💡 *RECOMENDACIÓN:*\n"
        msg += "• Locks con 4-5⭐ → Apuesta con confianza\n"
        msg += "• Locks con 3⭐ → Apuesta moderada\n"
        msg += "• Usar Kelly Criterion para stakes\n\n"

        msg += "⚠️ _Ninguna predicción es 100% segura._\n"
        msg += "⚠️ _Apuesta responsablemente._"

        return msg


if __name__ == '__main__':
    # Test del analizador de locks
    print("🧪 Testing Daily Locks Analyzer...\n")

    analyzer = DailyLocksAnalyzer()

    # Simular partidos de prueba
    test_matches = [
        {
            'home': 'Manchester City',
            'away': 'Sheffield United',
            'league': 'Premier League',
            'time': '15:00',
            'predictions': [
                {
                    'type': 'Ganador',
                    'prediction': 'Victoria Manchester City',
                    'recommended_bet': '1 (Victoria local)',
                    'confidence': 88,
                    'description': 'City es muy superior'
                }
            ]
        }
    ]

    locks = analyzer.find_daily_locks(test_matches, top_n=3)

    if locks:
        formatted = analyzer.format_locks_for_telegram(locks)
        print(formatted)
    else:
        print("No se encontraron locks")
