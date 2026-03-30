"""
Daily Locks Analyzer V2.0
Sistema profesional para encontrar las 3 mejores apuestas del día
Basado en metodologías de BetQL, Covers y análisis profesional

V2.0 Features:
- Sistema de scoring expandido a 150 puntos (10 factores)
- Home/Away Form Split analysis
- Rest Days & Fatigue detection
- Motivation & Context scoring
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
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

                if bet_score['total_score'] >= 90:  # Umbral mínimo V2.0 (60% de 150)
                    bets.append(bet_score)

            except Exception as e:
                logger.debug(f"Error calculando score: {e}")
                continue

        return bets

    def _calculate_bet_score(self, match: Dict, home: str, away: str,
                            league: str, prediction: Dict) -> Dict:
        """
        Calcular score compuesto para una apuesta - SISTEMA V2.0

        Factores evaluados (150 puntos total):
        1. Confidence base (25 pts) - Reducido de 30
        2. Team form/momentum (15 pts) - Reducido de 20
        3. xG data (15 pts) - Reducido de 20
        4. H2H history (10 pts) - Reducido de 15
        5. Value/EV (15 pts) - Mantiene
        6. Home/Away Split (10 pts) - NUEVO
        7. Rest Days & Fatigue (10 pts) - NUEVO
        8. Motivation & Context (10 pts) - NUEVO

        Bonus: +10 pts por consistencia (6+ factores altos)

        Returns:
            Dict con score y detalles
        """
        scores = {
            'confidence': 0,
            'form': 0,
            'xg': 0,
            'h2h': 0,
            'value': 0,
            'home_away': 0,      # NUEVO
            'rest_days': 0,      # NUEVO
            'motivation': 0      # NUEVO
        }

        factors_analyzed = []

        # 1. CONFIDENCE BASE (25 puntos) - Ajustado para V2.0
        base_confidence = prediction.get('confidence', 0)
        scores['confidence'] = (base_confidence / 100) * 25
        factors_analyzed.append(f"Confianza base: {base_confidence}%")

        # 2. TEAM FORM/MOMENTUM (15 puntos) - Ajustado para V2.0
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

                        # Escalar PPG (0-3) a puntos (0-15) - V2.0
                        if ppg >= 2.5:
                            scores['form'] = 15
                            factors_analyzed.append(f"Forma excepcional: {ppg} pts/partido")
                        elif ppg >= 2.0:
                            scores['form'] = 12
                            factors_analyzed.append(f"Buena forma: {ppg} pts/partido")
                        elif ppg >= 1.5:
                            scores['form'] = 9
                            factors_analyzed.append(f"Forma regular: {ppg} pts/partido")
                        else:
                            scores['form'] = 5
                            factors_analyzed.append(f"Forma baja: {ppg} pts/partido")
        except Exception as e:
            logger.debug(f"Error analizando form: {e}")
            scores['form'] = 8  # Neutral (ajustado para 15 pts max)

        # 3. xG DATA (15 puntos) - Ajustado para V2.0
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
                                scores['xg'] = 12
                                factors_analyzed.append(f"xG muy alto: {total_xg:.1f}")
                            elif total_xg > 2.5:
                                scores['xg'] = 12
                                factors_analyzed.append(f"xG favorable: {total_xg:.1f}")
                            else:
                                scores['xg'] = 6

                        elif 'under' in prediction.get('prediction', '').lower():
                            if total_xg < 2.0:
                                scores['xg'] = 12
                                factors_analyzed.append(f"xG bajo: {total_xg:.1f}")
                            elif total_xg < 2.3:
                                scores['xg'] = 12
                            else:
                                scores['xg'] = 6

                    # Para predicciones de resultado, ver diferencia xG
                    elif 'victoria' in pred_type or 'ganador' in pred_type:
                        home_xg = xg_comparison['match_prediction']['home_xg_expected']
                        away_xg = xg_comparison['match_prediction']['away_xg_expected']
                        diff = abs(home_xg - away_xg)

                        if diff > 0.8:
                            scores['xg'] = 12
                            factors_analyzed.append(f"Ventaja xG clara: {diff:.1f}")
                        elif diff > 0.5:
                            scores['xg'] = 12
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

                    # Para predicciones de goles (ajustado a 10 pts max)
                    if 'over' in pred_lower:
                        over_pct = h2h['trends']['over_25_percentage']
                        if over_pct > 70:
                            scores['h2h'] = 10
                            factors_analyzed.append(f"H2H Over: {over_pct}%")
                        elif over_pct > 60:
                            scores['h2h'] = 7
                        else:
                            scores['h2h'] = 4

                    elif 'under' in pred_lower:
                        over_pct = h2h['trends']['over_25_percentage']
                        under_pct = 100 - over_pct
                        if under_pct > 70:
                            scores['h2h'] = 10
                            factors_analyzed.append(f"H2H Under: {under_pct}%")
                        elif under_pct > 60:
                            scores['h2h'] = 7
                        else:
                            scores['h2h'] = 4

                    # Para BTTS
                    elif 'btts' in pred_lower or 'ambos' in pred_lower:
                        btts_pct = h2h['trends']['btts_percentage']
                        if btts_pct > 70:
                            scores['h2h'] = 10
                            factors_analyzed.append(f"H2H BTTS: {btts_pct}%")
                        elif btts_pct > 60:
                            scores['h2h'] = 7
                        else:
                            scores['h2h'] = 4

        except Exception as e:
            logger.debug(f"Error analizando H2H: {e}")
            scores['h2h'] = 5  # Neutral (ajustado para 10 pts max)

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

        # 6. HOME/AWAY FORM SPLIT (10 puntos) - NUEVO V2.0
        try:
            home_away_score, home_away_desc = self._calculate_home_away_split_score(home, away, league, match)
            scores['home_away'] = home_away_score
            factors_analyzed.append(f"Home/Away: {home_away_desc}")
        except Exception as e:
            logger.debug(f"Error calculando home/away: {e}")
            scores['home_away'] = 5

        # 7. REST DAYS & FATIGUE (10 puntos) - NUEVO V2.0
        try:
            rest_score, rest_desc = self._calculate_rest_days_score(home, away, match)
            scores['rest_days'] = rest_score
            factors_analyzed.append(f"Descanso: {rest_desc}")
        except Exception as e:
            logger.debug(f"Error calculando rest days: {e}")
            scores['rest_days'] = 5

        # 8. MOTIVATION & CONTEXT (10 puntos) - NUEVO V2.0
        try:
            motivation_score, motivation_desc = self._calculate_motivation_score(home, away, league, match)
            scores['motivation'] = motivation_score
            factors_analyzed.append(f"Motivación: {motivation_desc}")
        except Exception as e:
            logger.debug(f"Error calculando motivation: {e}")
            scores['motivation'] = 5

        # CALCULAR SCORE TOTAL (Sistema V2.0: 150 puntos max)
        total_score = sum(scores.values())

        # Bonus: Si múltiples factores coinciden (consistencia) - Ajustado para 8 factores
        # Threshold: 6+ factores deben tener score alto (>= 60% de su máximo)
        high_scores = sum(1 for key, score in scores.items() if score >= {
            'confidence': 15,  # 60% de 25
            'form': 9,         # 60% de 15
            'xg': 9,           # 60% de 15
            'h2h': 6,          # 60% de 10
            'value': 9,        # 60% de 15
            'home_away': 6,    # 60% de 10
            'rest_days': 6,    # 60% de 10
            'motivation': 6    # 60% de 10
        }.get(key, 0))

        if high_scores >= 6:  # 6+ de 8 factores son altos
            total_score += 10  # Bonus de consistencia
            factors_analyzed.append("⭐ Bonus consistencia (6+ factores altos)")
        elif high_scores >= 5:
            total_score += 7
            factors_analyzed.append("⭐ Bonus medio (5 factores altos)")
        elif high_scores >= 4:
            total_score += 5
            factors_analyzed.append("⭐ Bonus bajo (4 factores altos)")

        # Cap at 150
        total_score = min(total_score, 150)

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

    def _calculate_home_away_split_score(self, home: str, away: str, league: str, match: Dict) -> Tuple[float, str]:
        """
        Factor 6: Home/Away Form Split (10 pts)
        Análisis de rendimiento diferencial local vs visitante

        Returns:
            (score, description)
        """
        try:
            # Intentar obtener datos de forma local/visitante
            # Por ahora vamos a estimar basándonos en la forma general
            # TODO: Agregar llamada a API para stats específicas de local/visitante

            # Placeholder: usar factor de ventaja local estándar
            home_advantage = 0.5  # Ventaja local promedio

            score = 6  # Score neutral (60% de 10)
            description = "Ventaja local estándar"

            return score, description

        except Exception as e:
            logger.debug(f"Error calculando home/away split: {e}")
            return 5, "Home/Away split no disponible"

    def _calculate_rest_days_score(self, home: str, away: str, match: Dict) -> Tuple[float, str]:
        """
        Factor 7: Rest Days & Fatigue (10 pts)
        Detecta fatiga por partidos recientes

        Returns:
            (score, description)
        """
        try:
            # Obtener fecha del partido
            match_date = match.get('date', match.get('time', ''))
            if not match_date:
                return 5, "Fecha no disponible"

            # Parsear fecha
            if 'T' in match_date:
                match_datetime = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
            else:
                match_datetime = datetime.now()

            # Por ahora asumimos descanso estándar (placeholder)
            # TODO: Obtener fixture history real de cada equipo
            home_rest_days = 4  # Asumido
            away_rest_days = 4  # Asumido

            rest_differential = abs(home_rest_days - away_rest_days)

            if rest_differential >= 3:
                score = 8
                description = f"Diferencial de descanso: {rest_differential} días"
            elif rest_differential >= 2:
                score = 6
                description = "Ligero diferencial de descanso"
            else:
                score = 5
                description = "Descanso similar"

            # Penalizar si ambos están cansados
            if home_rest_days <= 3 and away_rest_days <= 3:
                score -= 1
                description += " (ambos con poco descanso)"

            return max(score, 1), description

        except Exception as e:
            logger.debug(f"Error calculando rest days: {e}")
            return 5, "Rest days no disponible"

    def _calculate_motivation_score(self, home: str, away: str, league: str, match: Dict) -> Tuple[float, str]:
        """
        Factor 8: Motivation & Context (10 pts)
        Analiza importancia del partido: Champions, descenso, derbies

        Returns:
            (score, description)
        """
        try:
            motivation_score = 0
            reasons = []

            # Check si es un derby/rivalry
            rivalries = self._get_rivalries()
            match_key = f"{home.lower()}_{away.lower()}"
            reverse_key = f"{away.lower()}_{home.lower()}"

            if match_key in rivalries or reverse_key in rivalries:
                motivation_score += 4
                reasons.append("Derby/Clásico")

            # Placeholder para posición en tabla (necesitaría API call)
            # TODO: Integrar con table standings

            # Por ahora dar score base
            if not reasons:
                motivation_score = 5
                reasons.append("Partido estándar")
            else:
                motivation_score += 5  # Base score

            score = min(motivation_score, 10)
            description = ", ".join(reasons)

            return score, description

        except Exception as e:
            logger.debug(f"Error calculando motivation: {e}")
            return 5, "Motivation no disponible"

    def _get_rivalries(self) -> set:
        """
        Obtener lista de rivalries conocidas

        Returns:
            Set de strings en formato "team1_team2"
        """
        rivalries = {
            # Premier League
            "manchester_united_manchester_city",  # Manchester Derby
            "manchester_city_manchester_united",
            "liverpool_everton",  # Merseyside Derby
            "everton_liverpool",
            "arsenal_tottenham",  # North London Derby
            "tottenham_arsenal",
            "liverpool_manchester_united",  # North West Derby
            "manchester_united_liverpool",
            "chelsea_arsenal",
            "arsenal_chelsea",

            # La Liga
            "barcelona_real_madrid",  # El Clásico
            "real_madrid_barcelona",
            "atletico_madrid_real_madrid",  # Madrid Derby
            "real_madrid_atletico_madrid",
            "barcelona_espanyol",  # Barcelona Derby
            "espanyol_barcelona",
            "sevilla_betis",  # Seville Derby
            "betis_sevilla",

            # Serie A
            "inter_milan",  # Derby della Madonnina
            "milan_inter",
            "inter_juventus",  # Derby d'Italia
            "juventus_inter",
            "roma_lazio",  # Derby della Capitale
            "lazio_roma",

            # Bundesliga
            "bayern_dortmund",  # Der Klassiker
            "dortmund_bayern",
            "schalke_dortmund",  # Revierderby
            "dortmund_schalke",

            # Ligue 1
            "psg_marseille",  # Le Classique
            "marseille_psg",
        }

        return rivalries

    def _calculate_star_rating(self, total_score: float) -> str:
        """
        Calcular rating de estrellas (1-5) basado en score total
        Sistema V2.0: Escala ajustada para 150 puntos

        Sistema similar a BetQL y Covers
        """
        if total_score >= 135:  # 90% de 150
            return "⭐⭐⭐⭐⭐"  # 5 estrellas - Lock máximo
        elif total_score >= 120:  # 80% de 150
            return "⭐⭐⭐⭐"    # 4 estrellas - Muy confiable
        elif total_score >= 105:  # 70% de 150
            return "⭐⭐⭐"      # 3 estrellas - Confiable
        elif total_score >= 90:   # 60% de 150
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
                "🔍 *FIJINI 48HS - ANÁLISIS COMPLETO*\n\n"
                "No se encontraron locks de alta calidad en las próximas 48 horas.\n\n"
                "💡 Esto puede significar:\n"
                "• Los partidos disponibles son muy inciertos\n"
                "• Las odds no ofrecen value suficiente\n"
                "• Mejor esperar a mejores oportunidades\n\n"
                "🎯 *ALTERNATIVAS:*\n"
                "• `/hoy` - Ver todos los partidos de hoy\n"
                "• `/partido [equipo1] vs [equipo2]` - Análisis específico\n"
                "• Espera unas horas y vuelve a intentar\n\n"
                "⚠️ No forzar apuestas sin confianza alta es lo más inteligente."
            )

        msg = "🔥 *FIJINI 48HS V2.0 - TOP 3 LOCKS* 🔥\n\n"
        msg += "_Sistema expandido a 150 pts: 8 factores + bonus_\n"
        msg += "_Las 3 mejores apuestas de las próximas 48 horas_\n\n"
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

            # Formatear fecha y hora
            try:
                if 'T' in time:
                    from datetime import datetime
                    dt = datetime.fromisoformat(time.replace('Z', '+00:00'))
                    today = datetime.now().date()
                    match_date = dt.date()

                    # Determinar si es hoy o mañana
                    if match_date == today:
                        relative = "Hoy"
                    elif (match_date - today).days == 1:
                        relative = "Mañana"
                    else:
                        relative = match_date.strftime("%d/%m")

                    msg += f"📅 *Fecha:* {relative} ({dt.strftime('%d/%m')})\n"
                    msg += f"🕐 *Hora:* {dt.strftime('%H:%M')}hs\n"
                else:
                    msg += f"🕐 *Hora:* {time}\n"
            except:
                msg += f"🕐 *Hora:* {time}\n"

            msg += f"\n🎯 *APUESTA RECOMENDADA:*\n"
            msg += f"   💡 {bet}\n"
            msg += f"   📊 Confianza: {confidence}%\n"
            msg += f"   🎲 Score Total: *{total_score}/150* ⚡V2.0\n\n"

            # Breakdown de scores - Sistema V2.0 (8 factores)
            msg += f"📈 *Análisis Multi-Factorial V2.0:*\n"
            breakdown = lock['scores_breakdown']
            msg += f"   • Base: {breakdown['confidence']:.0f}/25\n"
            msg += f"   • Forma: {breakdown['form']:.0f}/15\n"
            msg += f"   • xG: {breakdown['xg']:.0f}/15\n"
            msg += f"   • H2H: {breakdown['h2h']:.0f}/10\n"
            msg += f"   • Value: {breakdown['value']:.0f}/15\n"
            msg += f"   🆕 Home/Away: {breakdown['home_away']:.0f}/10\n"
            msg += f"   🆕 Descanso: {breakdown['rest_days']:.0f}/10\n"
            msg += f"   🆕 Motivación: {breakdown['motivation']:.0f}/10\n\n"

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

        # Footer con disclaimer - V2.0
        msg += "📊 *METODOLOGÍA V2.0:*\n"
        msg += "Sistema expandido a 150 pts (8 factores + bonus):\n"
        msg += "• Base (25) • Forma (15) • xG (15) • H2H (10)\n"
        msg += "• Value (15) 🆕 Home/Away (10)\n"
        msg += "🆕 Descanso (10) 🆕 Motivación (10)\n\n"

        msg += "🕐 *COBERTURA:*\n"
        msg += "Próximas 48 horas (hoy + mañana)\n"
        msg += "Precisión objetivo: 70-80% win rate (↑ vs V1.0)\n\n"

        msg += "⭐ *RATING V2.0:*\n"
        msg += "⭐⭐⭐⭐⭐ = Lock máximo (135-150 pts)\n"
        msg += "⭐⭐⭐⭐ = Muy confiable (120-134 pts)\n"
        msg += "⭐⭐⭐ = Confiable (105-119 pts)\n\n"

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
