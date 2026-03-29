"""
Value Bets System
Sistema profesional de detección de apuestas con valor
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ValueBetsAnalyzer:
    """Analizador de Value Bets"""

    # Mínimo Expected Value para recomendar
    MIN_EV_PERCENTAGE = 5.0

    # Mínimo de confianza en predicción para considerar value bet
    MIN_CONFIDENCE = 65

    def __init__(self, api_manager=None):
        """
        Inicializar analizador de value bets

        Args:
            api_manager: Gestor de APIs (opcional, para obtener odds)
        """
        self.api_manager = api_manager

    def calculate_value(self, predicted_probability: float, odds: float) -> Dict:
        """
        Calcular si una apuesta tiene valor

        Args:
            predicted_probability: Probabilidad predicha (0-100)
            odds: Cuota decimal de la casa de apuestas

        Returns:
            Diccionario con análisis de valor
        """
        # Convertir probabilidad a decimal si está en porcentaje
        if predicted_probability > 1:
            predicted_probability = predicted_probability / 100

        # Probabilidad implícita de las odds
        implied_probability = 1 / odds

        # Expected Value (Valor Esperado)
        # EV = (Probabilidad_Predicha * Cuota) - 1
        expected_value = (predicted_probability * odds) - 1

        # Margen de la casa (diferencia entre probabilidades)
        margin = implied_probability - predicted_probability

        # Es value bet si EV > 0 (preferible EV > 5%)
        is_value = expected_value > (self.MIN_EV_PERCENTAGE / 100)

        # Clasificación de valor
        if expected_value > 0.15:  # >15%
            value_rating = "🔥🔥🔥 EXCELENTE"
        elif expected_value > 0.10:  # >10%
            value_rating = "🔥🔥 MUY BUENO"
        elif expected_value > 0.05:  # >5%
            value_rating = "🔥 BUENO"
        elif expected_value > 0:  # >0%
            value_rating = "⚡ LEVE"
        else:
            value_rating = "❌ SIN VALOR"

        return {
            'predicted_probability': round(predicted_probability * 100, 1),
            'implied_probability': round(implied_probability * 100, 1),
            'expected_value': round(expected_value * 100, 2),
            'expected_value_decimal': round(expected_value, 4),
            'is_value_bet': is_value,
            'value_rating': value_rating,
            'margin': round(margin * 100, 2),
            'recommendation': self._generate_recommendation(expected_value, predicted_probability * 100)
        }

    def analyze_match_value(self, match_predictions: List[Dict], odds_data: Dict = None) -> List[Dict]:
        """
        Analizar value bets para todas las predicciones de un partido

        Args:
            match_predictions: Lista de predicciones del partido
            odds_data: Diccionario con odds de casas de apuestas

        Returns:
            Lista de value bets detectados
        """
        value_bets = []

        if not odds_data:
            logger.info("No hay odds disponibles para análisis de value")
            return value_bets

        # Mapeo de tipos de predicción a odds
        prediction_to_odds_map = {
            'victoria local': 'home_win',
            'gana': 'home_win',
            'victoria': 'home_win',
            'empate': 'draw',
            'over 2.5': 'over_25',
            'over': 'over_25',
            'under 2.5': 'under_25',
            'under': 'under_25',
        }

        for pred in match_predictions:
            if pred.get('confidence', 0) < self.MIN_CONFIDENCE:
                continue  # Solo analizar predicciones con confianza suficiente

            pred_type = pred.get('prediction', '').lower()
            confidence = pred.get('confidence', 0)

            # Buscar odds correspondiente
            odds_key = None
            for key, odds_field in prediction_to_odds_map.items():
                if key in pred_type:
                    odds_key = odds_field
                    break

            if not odds_key or odds_key not in odds_data:
                continue

            odds = odds_data[odds_key]
            if not odds or odds <= 1:
                continue

            # Calcular valor
            value_analysis = self.calculate_value(confidence, odds)

            if value_analysis['is_value_bet']:
                value_bet = {
                    **pred,
                    'odds': odds,
                    'value_analysis': value_analysis,
                    'is_value_bet': True
                }
                value_bets.append(value_bet)

        # Ordenar por EV (mejor primero)
        value_bets.sort(key=lambda x: x['value_analysis']['expected_value'], reverse=True)

        return value_bets

    def compare_bookmakers(self, market: str = 'h2h') -> Dict:
        """
        Comparar odds de múltiples casas de apuestas

        Args:
            market: Tipo de mercado (h2h, totals, btts)

        Returns:
            Comparación de odds
        """
        if not self.api_manager:
            return {'error': 'API manager no disponible'}

        try:
            # TODO: Implementar con The Odds API
            # Por ahora retornar estructura básica
            return {
                'market': market,
                'bookmakers': [],
                'best_odds': {},
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error comparando bookmakers: {e}")
            return {'error': str(e)}

    def calculate_kelly_criterion(self, predicted_probability: float, odds: float,
                                 kelly_fraction: float = 0.25) -> Dict:
        """
        Calcular tamaño óptimo de apuesta usando Kelly Criterion

        Args:
            predicted_probability: Probabilidad predicha (0-100)
            odds: Cuota decimal
            kelly_fraction: Fracción de Kelly a usar (default: 0.25 = 25% Kelly)

        Returns:
            Análisis de Kelly
        """
        # Convertir a decimal
        if predicted_probability > 1:
            predicted_probability = predicted_probability / 100

        # Kelly Criterion: (bp - q) / b
        # b = odds - 1 (ganancia neta)
        # p = probabilidad de ganar
        # q = probabilidad de perder (1 - p)

        b = odds - 1
        p = predicted_probability
        q = 1 - p

        # Cálculo Kelly
        kelly_percentage = (b * p - q) / b

        # Aplicar fracción de Kelly (más conservador)
        fractional_kelly = kelly_percentage * kelly_fraction

        # No apostar si Kelly es negativo o muy pequeño
        if kelly_percentage <= 0:
            return {
                'kelly_percentage': 0,
                'fractional_kelly': 0,
                'recommended_stake': 0,
                'recommendation': 'NO APOSTAR - Sin valor matemático'
            }

        # Limitar a máximo 10% del bankroll
        safe_stake = min(fractional_kelly, 0.10)

        return {
            'kelly_percentage': round(kelly_percentage * 100, 2),
            'fractional_kelly': round(fractional_kelly * 100, 2),
            'recommended_stake': round(safe_stake * 100, 2),
            'kelly_fraction_used': kelly_fraction,
            'recommendation': f'Apostar {round(safe_stake * 100, 1)}% del bankroll'
        }

    def detect_arbitrage(self, odds_home: float, odds_draw: float, odds_away: float) -> Dict:
        """
        Detectar oportunidad de arbitraje (surebet)

        Args:
            odds_home: Cuota victoria local
            odds_draw: Cuota empate
            odds_away: Cuota victoria visitante

        Returns:
            Análisis de arbitraje
        """
        # Suma de probabilidades implícitas
        total_implied_prob = (1/odds_home) + (1/odds_draw) + (1/odds_away)

        # Arbitraje existe si la suma < 1
        is_arbitrage = total_implied_prob < 1.0

        # Porcentaje de ganancia garantizada
        profit_percentage = ((1 / total_implied_prob) - 1) * 100 if is_arbitrage else 0

        if is_arbitrage:
            # Calcular stakes óptimos (para apuesta total de 100)
            total_stake = 100
            stake_home = (total_stake / odds_home) / total_implied_prob
            stake_draw = (total_stake / odds_draw) / total_implied_prob
            stake_away = (total_stake / odds_away) / total_implied_prob

            return {
                'is_arbitrage': True,
                'profit_percentage': round(profit_percentage, 2),
                'total_implied_probability': round(total_implied_prob * 100, 2),
                'stakes': {
                    'home': round(stake_home, 2),
                    'draw': round(stake_draw, 2),
                    'away': round(stake_away, 2)
                },
                'guaranteed_profit': round(profit_percentage, 2),
                'recommendation': f'⚡ ARBITRAJE DETECTADO: {profit_percentage:.2f}% ganancia garantizada'
            }
        else:
            return {
                'is_arbitrage': False,
                'profit_percentage': 0,
                'total_implied_probability': round(total_implied_prob * 100, 2),
                'margin': round((total_implied_prob - 1) * 100, 2),
                'recommendation': 'Sin oportunidad de arbitraje'
            }

    def _generate_recommendation(self, expected_value: float, confidence: float) -> str:
        """Generar recomendación basada en EV y confianza"""
        if expected_value > 0.15:
            return "✅ APOSTAR FUERTE - Excelente valor"
        elif expected_value > 0.10:
            return "✅ APOSTAR - Muy buen valor"
        elif expected_value > 0.05:
            return "✅ APOSTAR - Buen valor"
        elif expected_value > 0:
            return "⚡ CONSIDERAR - Valor leve"
        else:
            return "❌ NO APOSTAR - Sin valor"

    def format_value_bet_for_telegram(self, value_bet: Dict, bankroll: float = None) -> str:
        """
        Formatear value bet para mostrar en Telegram

        Args:
            value_bet: Diccionario con value bet
            bankroll: Bankroll del usuario (opcional)

        Returns:
            String formateado
        """
        pred = value_bet['prediction']
        conf = value_bet['confidence']
        odds = value_bet['odds']
        value = value_bet['value_analysis']

        msg = f"💰 *VALUE BET DETECTADO*\n\n"
        msg += f"🎯 *Predicción:* {pred}\n"
        msg += f"📊 *Tu confianza:* {conf}%\n"
        msg += f"💵 *Cuota:* {odds}\n\n"

        msg += f"📈 *ANÁLISIS DE VALOR:*\n"
        msg += f"   • Probabilidad predicha: {value['predicted_probability']}%\n"
        msg += f"   • Probabilidad implícita: {value['implied_probability']}%\n"
        msg += f"   • Expected Value: *+{value['expected_value']}%* {value['value_rating']}\n\n"

        # Kelly Criterion
        kelly = self.calculate_kelly_criterion(conf, odds)
        msg += f"💡 *GESTIÓN DE BANKROLL (Kelly Criterion):*\n"
        msg += f"   • {kelly['recommendation']}\n"

        if bankroll:
            stake_amount = bankroll * (kelly['recommended_stake'] / 100)
            potential_profit = stake_amount * (odds - 1)
            msg += f"   • Stake sugerido: ${stake_amount:.2f}\n"
            msg += f"   • Ganancia potencial: ${potential_profit:.2f}\n"

        msg += f"\n{value['recommendation']}"

        return msg


if __name__ == '__main__':
    # Test del sistema de value bets
    print("🧪 Testing Value Bets System...\n")

    analyzer = ValueBetsAnalyzer()

    # Test 1: Calcular valor individual
    print("=" * 60)
    print("Test 1: Value Bet Analysis")
    print("=" * 60)

    # Ejemplo: Predecimos 70% de ganar, casa ofrece 1.85
    value = analyzer.calculate_value(70, 1.85)
    print(f"Probabilidad predicha: {value['predicted_probability']}%")
    print(f"Probabilidad implícita (odds): {value['implied_probability']}%")
    print(f"Expected Value: {value['expected_value']}%")
    print(f"Rating: {value['value_rating']}")
    print(f"Recomendación: {value['recommendation']}")

    # Test 2: Kelly Criterion
    print("\n" + "=" * 60)
    print("Test 2: Kelly Criterion")
    print("=" * 60)

    kelly = analyzer.calculate_kelly_criterion(70, 1.85)
    print(f"Kelly %: {kelly['kelly_percentage']}%")
    print(f"Fractional Kelly (25%): {kelly['fractional_kelly']}%")
    print(f"Stake recomendado: {kelly['recommended_stake']}%")
    print(f"Recomendación: {kelly['recommendation']}")

    # Test 3: Arbitraje
    print("\n" + "=" * 60)
    print("Test 3: Arbitrage Detection")
    print("=" * 60)

    # Ejemplo de arbitraje (suma < 1)
    arb = analyzer.detect_arbitrage(2.10, 3.50, 3.80)
    print(f"¿Es arbitraje?: {arb['is_arbitrage']}")
    print(f"Ganancia: {arb['profit_percentage']}%")
    print(f"Recomendación: {arb['recommendation']}")

    if arb['is_arbitrage']:
        print(f"\nStakes para apuesta de $100:")
        print(f"  Local: ${arb['stakes']['home']}")
        print(f"  Empate: ${arb['stakes']['draw']}")
        print(f"  Visitante: ${arb['stakes']['away']}")
