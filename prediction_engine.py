"""
Advanced Prediction Engine
Motor de predicciones avanzado con análisis real
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PredictionEngine:
    """Motor de predicciones con análisis avanzado"""

    def __init__(self, api_manager=None):
        """Inicializar motor de predicciones"""
        self.api_manager = api_manager
        self.xg_analyzer = None
        self.value_bets_analyzer = None
        self.data_fetcher = None
        self.ml_predictor = None
        self._init_analyzers()

    def _init_analyzers(self):
        """Inicializar analizadores avanzados"""
        # Data Fetcher
        try:
            from data_fetcher import DataFetcher
            self.data_fetcher = DataFetcher()
            logger.info("Data Fetcher inicializado")
        except Exception as e:
            logger.warning(f"Data Fetcher no disponible: {e}")

        # xG Analyzer
        try:
            from xg_analyzer import xGAnalyzer
            self.xg_analyzer = xGAnalyzer()
            logger.info("xG Analyzer inicializado")
        except Exception as e:
            logger.warning(f"xG Analyzer no disponible: {e}")

        # Value Bets Analyzer
        try:
            from value_bets import ValueBetsAnalyzer
            self.value_bets_analyzer = ValueBetsAnalyzer(self.api_manager)
            logger.info("Value Bets Analyzer inicializado")
        except Exception as e:
            logger.warning(f"Value Bets Analyzer no disponible: {e}")

        # ML Predictor
        try:
            from ml_model import MLPredictor
            self.ml_predictor = MLPredictor()
            if self.ml_predictor.is_model_trained():
                logger.info("🤖 ML Predictor inicializado con modelos cargados")
            else:
                logger.warning("ML Predictor inicializado pero sin modelos entrenados")
        except Exception as e:
            logger.warning(f"ML Predictor no disponible: {e}")

    def analyze_match(self, home_team: str, away_team: str, league: str = None) -> Dict:
        """
        Analizar partido y generar predicciones completas

        Args:
            home_team: Equipo local
            away_team: Equipo visitante
            league: Liga del partido

        Returns:
            Diccionario con análisis completo
        """
        try:
            # Intentar obtener datos xG reales primero
            xg_data = None
            if self.xg_analyzer and league:
                try:
                    xg_data = self.xg_analyzer.compare_teams_xg(home_team, away_team, league)
                    if 'error' in xg_data:
                        xg_data = None
                    else:
                        logger.info(f"✓ Datos xG obtenidos para {home_team} vs {away_team}")
                except Exception as e:
                    logger.warning(f"No se pudo obtener xG: {e}")

            # Analizar fortalezas de equipos
            home_strength = self._analyze_team_strength(home_team, league)
            away_strength = self._analyze_team_strength(away_team, league)

            # Si tenemos datos xG, actualizar las fortalezas
            if xg_data:
                home_stats = xg_data['home_stats']
                away_stats = xg_data['away_stats']

                # Actualizar ataque basado en xG real
                home_strength['attack'] = min(int(home_stats['xg_for_avg'] * 35) + 30, 100)
                away_strength['attack'] = min(int(away_stats['xg_for_avg'] * 35) + 30, 100)

                # Actualizar defensa basado en xG concedido
                home_strength['defense'] = max(100 - int(home_stats['xg_against_avg'] * 30), 50)
                away_strength['defense'] = max(100 - int(away_stats['xg_against_avg'] * 30), 50)

            # Obtener odds reales desde The Odds API
            odds_data = None
            if self.data_fetcher:
                try:
                    odds_data = self.data_fetcher.get_real_odds(home_team, away_team)
                    if odds_data:
                        logger.info(f"Real odds obtained for {home_team} vs {away_team} from {odds_data.get('bookmaker', 'bookmaker')}")
                    else:
                        logger.debug(f"No real odds available for {home_team} vs {away_team}")
                except Exception as e:
                    logger.warning(f"Error fetching real odds: {e}")

            # Obtener predicción ML (Base Confidence)
            ml_analysis = None
            if self.ml_predictor and self.ml_predictor.is_model_trained():
                try:
                    ml_analysis = self.ml_predictor.predict_match(
                        home_team, away_team, league, xg_data, odds_data
                    )
                    if ml_analysis and ml_analysis.get('model_available'):
                        logger.info(f"✓ ML prediction: {ml_analysis['ml_confidence']}% confidence")
                except Exception as e:
                    logger.warning(f"Error en predicción ML: {e}")

            # Generar predicciones
            predictions = self._generate_predictions(
                home_team, away_team,
                home_strength, away_strength,
                xg_data=xg_data,
                ml_analysis=ml_analysis
            )

            result = {
                'home_team': home_team,
                'away_team': away_team,
                'home_strength': home_strength,
                'away_strength': away_strength,
                'predictions': predictions,
                'timestamp': datetime.now().isoformat()
            }

            # Agregar datos xG si están disponibles
            if xg_data:
                result['xg_analysis'] = xg_data
                result['uses_real_xg'] = True

            # Agregar análisis ML si está disponible
            if ml_analysis:
                result['ml_analysis'] = ml_analysis
                result['uses_ml'] = True

            # Analizar value bets si tenemos odds
            if odds_data and self.value_bets_analyzer:
                try:
                    value_bets = self.value_bets_analyzer.analyze_match_value(predictions, odds_data)
                    if value_bets:
                        result['value_bets'] = value_bets
                        result['has_value_bets'] = True
                        logger.info(f"✓ {len(value_bets)} value bets detectados")
                except Exception as e:
                    logger.warning(f"Error analizando value bets: {e}")

            # Agregar odds si están disponibles
            if odds_data:
                result['odds'] = odds_data

            return result

        except Exception as e:
            logger.error(f"Error analizando partido: {e}")
            return self._generate_basic_predictions(home_team, away_team)

    def _analyze_team_strength(self, team_name: str, league: str = None) -> Dict:
        """
        Analizar fortaleza del equipo usando DataFetcher

        Returns:
            Diccionario con métricas del equipo
        """
        # Si DataFetcher está disponible, usarlo
        if self.data_fetcher:
            return self.data_fetcher.get_team_strength(team_name, league)

        # Fallback si DataFetcher no está disponible
        # Valores predeterminados conservadores
        logger.warning(f"DataFetcher not available, using default values for {team_name}")
        return {
            'attack': 72,
            'defense': 72,
            'form': 72
        }

    def _generate_predictions(self, home_team: str, away_team: str,
                            home_strength: Dict, away_strength: Dict,
                            xg_data: Dict = None, ml_analysis: Dict = None) -> List[Dict]:
        """
        Generar predicciones basadas en análisis

        Sistema de Scoring (100 puntos):
        1. Base Confidence (30 pts) ← ML model
        2. Form/Momentum (20 pts)
        3. xG real (20 pts)
        4. H2H (15 pts)
        5. Expected Value (15 pts)

        Returns:
            Lista de predicciones ordenadas por confianza
        """
        predictions = []

        # Base Confidence desde ML (30 puntos máximo)
        ml_base_confidence = 0
        if ml_analysis and ml_analysis.get('model_available'):
            ml_base_confidence = min(int(ml_analysis['ml_confidence'] * 0.30), 30)
            logger.debug(f"ML Base Confidence: {ml_base_confidence}/30 pts")
        else:
            # Fallback: base confidence de 15 pts (50% de 30)
            ml_base_confidence = 15
            logger.debug("Usando fallback base confidence: 15/30 pts")

        # Calcular diferencias
        home_attack = home_strength['attack']
        away_defense = away_strength['defense']
        away_attack = away_strength['attack']
        home_defense = home_strength['defense']

        home_form = home_strength['form']
        away_form = away_strength['form']

        # 1. PREDICCIÓN DE RESULTADO
        # Usar ML probs si están disponibles, sino fallback
        home_advantage = 5  # Ventaja de local
        home_total = home_attack + home_defense + home_form + home_advantage
        away_total = away_attack + away_defense + away_form

        diff = home_total - away_total

        # Form/Momentum score (20 pts max)
        form_score = int((home_form + away_form) / 10)  # 0-20

        # xG score (20 pts max) - si hay xG data
        xg_score = 0
        if xg_data and 'match_prediction' in xg_data:
            xg_confidence = xg_data['match_prediction'].get('confidence', 0)
            xg_score = int(xg_confidence * 0.20)  # max 20

        # Total confidence = Base (30) + Form (20) + xG (20) + H2H (15) + EV (15)
        # Por ahora H2H y EV no están implementados, usamos simplificación

        if diff > 15:
            base_conf = ml_base_confidence + form_score + xg_score
            predictions.append({
                'type': '🏆 Ganador',
                'prediction': f'Gana {home_team}',
                'confidence': min(base_conf + 15, 95),  # +15 por ventaja clara
                'description': f'{home_team} es claramente superior',
                'bet_type': 'Resultado',
                'recommended_bet': f'1 (Victoria {home_team})'
            })
        elif diff < -15:
            base_conf = ml_base_confidence + form_score + xg_score
            predictions.append({
                'type': '🏆 Ganador',
                'prediction': f'Gana {away_team}',
                'confidence': min(base_conf + 15, 95),
                'description': f'{away_team} es claramente superior',
                'bet_type': 'Resultado',
                'recommended_bet': f'2 (Victoria {away_team})'
            })
        elif abs(diff) <= 10:
            base_conf = ml_base_confidence + form_score + xg_score
            predictions.append({
                'type': '🤝 Empate/Doble Chance',
                'prediction': 'Partido parejo',
                'confidence': min(base_conf + 5, 85),
                'description': 'Ambos equipos equilibrados',
                'bet_type': 'Resultado',
                'recommended_bet': 'X (Empate) o 1X/X2 (Doble Chance)'
            })
        else:
            winner = home_team if diff > 0 else away_team
            base_conf = ml_base_confidence + form_score + xg_score
            predictions.append({
                'type': '⚖️ Favorito',
                'prediction': f'Favorito: {winner}',
                'confidence': min(base_conf + 10, 88),
                'description': f'{winner} tiene ventaja pero no es seguro',
                'bet_type': 'Resultado',
                'recommended_bet': f'{"1" if diff > 0 else "2"} o 1X/X2'
            })

        # 2. PREDICCIÓN DE GOLES
        # Usar ML prediction si está disponible
        if ml_analysis and ml_analysis.get('model_available'):
            avg_goals_expected = ml_analysis.get('ml_predicted_goals', 2.5)
            over_25_prob = ml_analysis.get('ml_over_2_5_prob', 50)
            logger.info(f"Usando ML: {avg_goals_expected:.2f} goles esperados, Over 2.5: {over_25_prob}%")
        elif xg_data and 'match_prediction' in xg_data:
            avg_goals_expected = xg_data['match_prediction']['total_xg_expected']
            over_25_prob = 60 if avg_goals_expected > 2.7 else 40
            logger.info(f"Usando xG real: {avg_goals_expected:.2f} goles esperados")
        else:
            avg_goals_expected = (home_attack + away_attack) / 40  # Escala a goles esperados
            over_25_prob = 50

        # Confidence con scoring system
        base_goals_conf = ml_base_confidence + form_score + xg_score

        if avg_goals_expected > 2.7 or over_25_prob > 55:
            predictions.append({
                'type': '⚽ Goles',
                'prediction': 'Over 2.5 goles',
                'confidence': min(base_goals_conf + int((avg_goals_expected - 2.5) * 5), 92),
                'description': f'Ambos equipos ofensivos ({avg_goals_expected:.1f} goles esperados)',
                'bet_type': 'Goles',
                'recommended_bet': 'Over 2.5 goles'
            })
        elif avg_goals_expected < 2.2 or over_25_prob < 45:
            predictions.append({
                'type': '🔒 Goles',
                'prediction': 'Under 2.5 goles',
                'confidence': min(base_goals_conf + int((2.5 - avg_goals_expected) * 5), 90),
                'description': f'Partido cerrado ({avg_goals_expected:.1f} goles esperados)',
                'bet_type': 'Goles',
                'recommended_bet': 'Under 2.5 goles'
            })
        else:
            predictions.append({
                'type': '⚽ Goles',
                'prediction': f'Entre 2-3 goles',
                'confidence': min(base_goals_conf, 75),
                'description': f'Goles esperados: {avg_goals_expected:.1f}',
                'bet_type': 'Goles',
                'recommended_bet': 'Over/Under según cuotas'
            })

        # 3. AMBOS ANOTAN (BTTS)
        both_attack_strong = home_attack > 75 and away_attack > 75
        both_defense_weak = home_defense < 80 and away_defense < 80

        # Usar ML BTTS prob si está disponible
        btts_yes_prob = 50
        if ml_analysis and ml_analysis.get('model_available'):
            btts_yes_prob = ml_analysis.get('ml_btts_yes_prob', 50)

        base_btts_conf = ml_base_confidence + form_score + xg_score

        if both_attack_strong or both_defense_weak or btts_yes_prob > 55:
            conf_boost = 10 if both_attack_strong else 5
            predictions.append({
                'type': '🎯 Ambos Anotan',
                'prediction': 'Sí - Ambos equipos marcarán',
                'confidence': min(base_btts_conf + conf_boost, 88),
                'description': f'Ambos equipos tienen capacidad ofensiva (BTTS prob: {btts_yes_prob:.0f}%)',
                'bet_type': 'Ambos Anotan',
                'recommended_bet': 'Sí (BTTS - Both Teams To Score)'
            })
        elif (home_defense > 85 or away_defense > 85) or btts_yes_prob < 45:
            predictions.append({
                'type': '🛡️ Ambos Anotan',
                'prediction': 'No - Defensas sólidas',
                'confidence': min(base_btts_conf + 5, 82),
                'description': f'Al menos una defensa sólida (BTTS prob: {btts_yes_prob:.0f}%)',
                'bet_type': 'Ambos Anotan',
                'recommended_bet': 'No (al menos un equipo no anotará)'
            })

        # 4. TARJETAS (si el partido es parejo e intenso)
        if abs(diff) < 8 and (home_form > 80 or away_form > 80):
            predictions.append({
                'type': '🟨 Tarjetas',
                'prediction': 'Partido intenso',
                'confidence': 68,
                'description': 'Partido parejo y competitivo',
                'bet_type': 'Tarjetas',
                'recommended_bet': 'Over 4.5 tarjetas'
            })

        # 5. CÓRNERS (equipos ofensivos)
        if home_attack > 82 or away_attack > 82:
            predictions.append({
                'type': '🚩 Córners',
                'prediction': 'Muchos córners esperados',
                'confidence': 72,
                'description': 'Equipos con mucha presión ofensiva',
                'bet_type': 'Córners',
                'recommended_bet': 'Over 9.5 córners'
            })

        # Ordenar por confianza
        predictions.sort(key=lambda x: x['confidence'], reverse=True)

        return predictions

    def _generate_basic_predictions(self, home_team: str, away_team: str) -> Dict:
        """Predicciones básicas cuando no hay datos suficientes"""
        return {
            'home_team': home_team,
            'away_team': away_team,
            'predictions': [{
                'type': 'ℹ️ Info',
                'prediction': 'Análisis limitado',
                'confidence': 0,
                'description': 'Datos insuficientes para predicción confiable',
                'bet_type': 'N/A',
                'recommended_bet': 'Esperar más información'
            }]
        }

    def format_predictions_for_telegram(self, analysis: Dict) -> str:
        """
        Formatear análisis para mostrar en Telegram

        Args:
            analysis: Diccionario con análisis completo

        Returns:
            String formateado para Telegram
        """
        home = analysis['home_team']
        away = analysis['away_team']
        predictions = analysis.get('predictions', [])

        msg = f"⚽ *{home} vs {away}*\n\n"

        if 'home_strength' in analysis:
            home_s = analysis['home_strength']
            away_s = analysis['away_strength']

            msg += "📊 *Análisis de Equipos:*\n"
            msg += f"🏠 {home}:\n"
            msg += f"   Ataque: {home_s['attack']}/100 | Defensa: {home_s['defense']}/100\n"
            msg += f"🚗 {away}:\n"
            msg += f"   Ataque: {away_s['attack']}/100 | Defensa: {away_s['defense']}/100\n\n"

        # Mostrar odds si están disponibles
        if 'odds' in analysis and analysis['odds']:
            odds = analysis['odds']
            msg += "💵 *CUOTAS:*\n"
            if odds.get('home_win'):
                msg += f"   🏠 Local: {odds['home_win']}\n"
            if odds.get('draw'):
                msg += f"   ➖ Empate: {odds['draw']}\n"
            if odds.get('away_win'):
                msg += f"   🚗 Visitante: {odds['away_win']}\n"
            if odds.get('over_25'):
                msg += f"   📈 Over 2.5: {odds['over_25']}\n"
            if odds.get('under_25'):
                msg += f"   📉 Under 2.5: {odds['under_25']}\n"
            msg += f"   _Casa: {odds.get('bookmaker', 'N/A')}_\n\n"

        # Mostrar value bets si hay
        if analysis.get('has_value_bets') and analysis.get('value_bets'):
            msg += "💰 *VALUE BETS DETECTADOS:*\n\n"

            for i, vb in enumerate(analysis['value_bets'][:3], 1):  # Top 3 value bets
                val = vb['value_analysis']
                msg += f"*{i}. {vb['prediction']}* {val['value_rating']}\n"
                msg += f"   💵 Cuota: {vb['odds']}\n"
                msg += f"   📊 Tu predicción: {val['predicted_probability']}%\n"
                msg += f"   📈 Expected Value: *+{val['expected_value']}%*\n"
                msg += f"   ✅ {val['recommendation']}\n\n"

            msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

        msg += "🎯 *RECOMENDACIONES DE APUESTAS:*\n\n"

        for i, pred in enumerate(predictions[:5], 1):  # Top 5 predicciones
            confidence = pred.get('confidence', 0)

            # Emoji de confianza
            if confidence >= 85:
                conf_emoji = "🔥🔥🔥"
            elif confidence >= 75:
                conf_emoji = "🔥🔥"
            elif confidence >= 65:
                conf_emoji = "✅"
            else:
                conf_emoji = "⚠️"

            msg += f"*{i}. {pred['type']}* {conf_emoji}\n"
            msg += f"   💡 {pred['prediction']}\n"
            msg += f"   🎲 Apostar: *{pred['recommended_bet']}*\n"
            msg += f"   📈 Confianza: {confidence}%\n"
            msg += f"   ℹ️ {pred['description']}\n\n"

        # Notas sobre mejoras
        if analysis.get('uses_ml'):
            ml_data = analysis.get('ml_analysis', {})
            ml_conf = ml_data.get('ml_confidence', 0)
            msg += f"\n🤖 _Predicción potenciada con ML (confidence: {ml_conf}%)_\n"

        if analysis.get('uses_real_xg'):
            msg += "📊 _Análisis mejorado con datos xG reales_\n"

        msg += "⚠️ _Apuesta responsablemente_"

        return msg


if __name__ == '__main__':
    # Test del motor de predicciones
    print("🧪 Testing Prediction Engine...\n")

    engine = PredictionEngine()

    # Test: Colombia vs Francia
    print("=" * 50)
    print("Partido: Colombia vs France")
    print("=" * 50)

    analysis = engine.analyze_match('Colombia', 'France')

    for pred in analysis['predictions']:
        print(f"\n{pred['type']}: {pred['prediction']}")
        print(f"Confianza: {pred['confidence']}%")
        print(f"Apuesta: {pred['recommended_bet']}")
        print(f"Razón: {pred['description']}")
