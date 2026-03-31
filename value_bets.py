"""
Value Bets System - Real odds and Poisson model
Sistema profesional de detección de value bets con datos reales
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import math
from scipy.stats import poisson

from data_fetcher import DataFetcher

logger = logging.getLogger(__name__)


class ValueBetFinder:
    """
    Analizador de Value Bets usando modelo Poisson y datos reales
    """

    # Mínimo Expected Value para considerar value bet (5%)
    MIN_EV_THRESHOLD = 0.05

    def __init__(self):
        """Inicializar value bet finder con data fetcher"""
        self.data_fetcher = DataFetcher()
        logger.info("ValueBetFinder inicializado con DataFetcher")

    def _poisson_probabilities(self, lambda_home: float, lambda_away: float) -> Dict[str, float]:
        """
        Calcular probabilidades de resultados usando distribución de Poisson

        Args:
            lambda_home: Lambda (media esperada de goles) del equipo local
            lambda_away: Lambda (media esperada de goles) del equipo visitante

        Returns:
            Dict con probabilidades de home_win, draw, away_win
        """
        # Calcular probabilidades para diferentes scorelines
        # Consideramos hasta 5 goles por equipo (cubre ~99% de los casos)
        max_goals = 5

        prob_home_win = 0.0
        prob_draw = 0.0
        prob_away_win = 0.0

        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                # P(home_goals) * P(away_goals)
                prob = poisson.pmf(home_goals, lambda_home) * poisson.pmf(away_goals, lambda_away)

                if home_goals > away_goals:
                    prob_home_win += prob
                elif home_goals == away_goals:
                    prob_draw += prob
                else:
                    prob_away_win += prob

        return {
            'home_win': prob_home_win,
            'draw': prob_draw,
            'away_win': prob_away_win
        }

    def analyze_match(
        self,
        home_team: str,
        away_team: str,
        home_odds: float,
        away_odds: float,
        draw_odds: float,
        competition_id: int = 2021
    ) -> Dict:
        """
        Analizar un partido y calcular Expected Value

        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante
            home_odds: Odds para victoria local (decimal)
            away_odds: Odds para victoria visitante (decimal)
            draw_odds: Odds para empate (decimal)
            competition_id: ID de la competición (default: Premier League)

        Returns:
            Dict con análisis completo:
            {
                'home_ev': float,
                'draw_ev': float,
                'away_ev': float,
                'recommendation': str,
                'confidence': float,
                'best_bet': str,
                'probabilities_model': dict,
                'probabilities_implied': dict,
                'stats': dict
            }
        """
        logger.info(f"Analizando: {home_team} vs {away_team}")

        # 1. Obtener team IDs
        home_team_id = self.data_fetcher.get_team_id(home_team, competition_id)
        away_team_id = self.data_fetcher.get_team_id(away_team, competition_id)

        if not home_team_id or not away_team_id:
            logger.warning(f"No se encontraron IDs para los equipos")
            return {
                'error': 'Teams not found',
                'home_ev': 0,
                'draw_ev': 0,
                'away_ev': 0,
                'recommendation': 'NO BET - Teams not found',
                'confidence': 0
            }

        # 2. Obtener stats reales de ambos equipos
        home_stats = self.data_fetcher.get_team_stats(home_team_id)
        away_stats = self.data_fetcher.get_team_stats(away_team_id)

        logger.info(f"Stats {home_team}: ATK={home_stats['attack']} DEF={home_stats['defense']} FORM={home_stats['form']}")
        logger.info(f"Stats {away_team}: ATK={away_stats['attack']} DEF={away_stats['defense']} FORM={away_stats['form']}")

        # 3. Calcular lambdas para Poisson
        # lambda_home = (attack_home/100) * (defense_away/100) * factor_home_advantage
        # lambda_away = (attack_away/100) * (defense_home/100)
        # Normalizamos: asumimos que 70/100 = 1.4 goles promedio

        # Factor de ventaja de local (típicamente 1.3x)
        home_advantage = 1.3

        # Convertir stats (0-100) a goles esperados
        # Attack 70 = ~1.4 goles, Attack 100 = ~2.5 goles
        # Defense 70 = permite ~1.4 goles, Defense 100 = permite ~0.8 goles

        attack_home_factor = (home_stats['attack'] / 100) * 2.0  # Max ~2.0 goles base
        defense_away_factor = 1.0 - (away_stats['defense'] / 100) * 0.5  # Multiplier 0.5-1.0

        attack_away_factor = (away_stats['attack'] / 100) * 2.0
        defense_home_factor = 1.0 - (home_stats['defense'] / 100) * 0.5

        lambda_home = attack_home_factor * defense_away_factor * home_advantage
        lambda_away = attack_away_factor * defense_home_factor

        # Ajustar por forma
        form_home_multiplier = 0.8 + (home_stats['form'] / 100) * 0.4  # 0.8 - 1.2
        form_away_multiplier = 0.8 + (away_stats['form'] / 100) * 0.4

        lambda_home *= form_home_multiplier
        lambda_away *= form_away_multiplier

        logger.info(f"Lambdas calculadas: λ_home={lambda_home:.2f}, λ_away={lambda_away:.2f}")

        # 4. Calcular probabilidades con Poisson
        probs_model = self._poisson_probabilities(lambda_home, lambda_away)

        logger.info(f"Probabilidades modelo: HOME={probs_model['home_win']:.3f} DRAW={probs_model['draw']:.3f} AWAY={probs_model['away_win']:.3f}")

        # 5. Calcular probabilidades implícitas de las odds
        prob_home_implied = 1 / home_odds
        prob_draw_implied = 1 / draw_odds
        prob_away_implied = 1 / away_odds

        # 6. Calcular Expected Value para cada outcome
        # EV = (prob_propia * odd_real) - 1
        home_ev = (probs_model['home_win'] * home_odds) - 1
        draw_ev = (probs_model['draw'] * draw_odds) - 1
        away_ev = (probs_model['away_win'] * away_odds) - 1

        logger.info(f"Expected Values: HOME={home_ev:.3f} DRAW={draw_ev:.3f} AWAY={away_ev:.3f}")

        # 7. Determinar mejor apuesta
        best_ev = max(home_ev, draw_ev, away_ev)

        if best_ev == home_ev:
            best_bet = 'HOME'
            best_odds = home_odds
            best_prob = probs_model['home_win']
        elif best_ev == draw_ev:
            best_bet = 'DRAW'
            best_odds = draw_odds
            best_prob = probs_model['draw']
        else:
            best_bet = 'AWAY'
            best_odds = away_odds
            best_prob = probs_model['away_win']

        # 8. Generar recomendación
        if best_ev > 0.15:
            recommendation = f"🔥🔥🔥 STRONG VALUE BET - {best_bet}"
            confidence = 95
        elif best_ev > 0.10:
            recommendation = f"🔥🔥 GOOD VALUE BET - {best_bet}"
            confidence = 85
        elif best_ev > 0.05:
            recommendation = f"🔥 VALUE BET - {best_bet}"
            confidence = 75
        elif best_ev > 0:
            recommendation = f"⚡ SMALL VALUE - {best_bet}"
            confidence = 60
        else:
            recommendation = "❌ NO VALUE - Skip this match"
            confidence = 0

        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_ev': round(home_ev, 4),
            'draw_ev': round(draw_ev, 4),
            'away_ev': round(away_ev, 4),
            'best_bet': best_bet,
            'best_ev': round(best_ev, 4),
            'best_odds': best_odds,
            'best_prob': round(best_prob * 100, 1),
            'recommendation': recommendation,
            'confidence': confidence,
            'probabilities_model': {
                'home_win': round(probs_model['home_win'] * 100, 1),
                'draw': round(probs_model['draw'] * 100, 1),
                'away_win': round(probs_model['away_win'] * 100, 1)
            },
            'probabilities_implied': {
                'home_win': round(prob_home_implied * 100, 1),
                'draw': round(prob_draw_implied * 100, 1),
                'away_win': round(prob_away_implied * 100, 1)
            },
            'stats': {
                'home': home_stats,
                'away': away_stats,
                'lambda_home': round(lambda_home, 2),
                'lambda_away': round(lambda_away, 2)
            }
        }

    def find_value_in_competition(self, competition_id: int = 2021) -> List[Dict]:
        """
        Encontrar value bets en una competición usando odds reales

        Obtiene próximos partidos y busca odds reales desde The Odds API.
        Solo retorna partidos con EV > 5%.

        Args:
            competition_id: ID de la competición

        Returns:
            Lista de partidos con value bets (EV > 5%)
        """
        logger.info(f"Buscando value bets en competición {competition_id}")

        # Obtener próximos partidos
        upcoming = self.data_fetcher.get_upcoming_matches(competition_id, days_ahead=7)
        logger.info(f"Próximos partidos encontrados: {len(upcoming)}")

        if not upcoming:
            logger.warning("No hay próximos partidos en esta competición")
            return []

        value_bets = []
        matches_analyzed = 0
        matches_skipped = 0

        for match in upcoming:
            home_team = match['home_team']
            away_team = match['away_team']

            logger.info(f"Analizando: {home_team} vs {away_team}")

            # Verificar límite de requests antes de continuar
            if self.data_fetcher.odds_requests_remaining is not None:
                if self.data_fetcher.odds_requests_remaining < 50:
                    logger.warning(f"⚠️ PAUSA: Solo quedan {self.data_fetcher.odds_requests_remaining} requests")
                    logger.warning(f"Analizados: {matches_analyzed} | Skipped: {matches_skipped}")
                    break

            # Obtener odds reales
            odds = self.data_fetcher.get_real_odds(home_team, away_team)

            if not odds:
                logger.info(f"No odds available para {home_team} vs {away_team} - skipping")
                matches_skipped += 1
                continue

            # Analizar con odds reales
            try:
                analysis = self.analyze_match(
                    home_team=home_team,
                    away_team=away_team,
                    home_odds=odds['home_win'],
                    away_odds=odds['away_win'],
                    draw_odds=odds['draw'],
                    competition_id=competition_id
                )

                matches_analyzed += 1

                # Solo guardar si tiene value (EV > 5%)
                if analysis['best_ev'] > self.MIN_EV_THRESHOLD:
                    analysis['match_date'] = match['date']
                    analysis['bookmaker'] = odds['bookmaker']
                    value_bets.append(analysis)
                    logger.info(f"✓ VALUE BET: {analysis['best_bet']} con EV={analysis['best_ev']*100:.1f}%")
                else:
                    logger.info(f"✗ No value: mejor EV={analysis['best_ev']*100:.1f}%")

            except Exception as e:
                logger.error(f"Error analizando {home_team} vs {away_team}: {e}")
                matches_skipped += 1
                continue

        # Ordenar por mejor EV
        value_bets.sort(key=lambda x: x['best_ev'], reverse=True)

        logger.info(f"Análisis completado: {matches_analyzed} analizados, {matches_skipped} skipped")
        logger.info(f"Value bets encontrados: {len(value_bets)}")

        if self.data_fetcher.odds_requests_remaining:
            logger.info(f"Requests restantes: {self.data_fetcher.odds_requests_remaining}")

        return value_bets

    def format_telegram_message(self, bet: Dict) -> str:
        """
        Formatear resultado para Telegram

        Args:
            bet: Diccionario con análisis del partido

        Returns:
            Mensaje formateado para Telegram
        """
        if 'error' in bet:
            return f"❌ Error: {bet['error']}"

        msg = f"⚽ *{bet['home_team']} vs {bet['away_team']}*\n\n"

        msg += f"🎯 *RECOMENDACIÓN:*\n"
        msg += f"{bet['recommendation']}\n"
        msg += f"Confianza: {bet['confidence']}%\n\n"

        if bet['confidence'] > 0:
            msg += f"💰 *MEJOR APUESTA: {bet['best_bet']}*\n"
            msg += f"   • Odds: {bet['best_odds']}\n"
            msg += f"   • Expected Value: +{bet['best_ev']*100:.1f}%\n"
            msg += f"   • Probabilidad modelo: {bet['best_prob']}%\n\n"

        msg += f"📊 *EXPECTED VALUES:*\n"
        msg += f"   • HOME: {bet['home_ev']*100:+.1f}%\n"
        msg += f"   • DRAW: {bet['draw_ev']*100:+.1f}%\n"
        msg += f"   • AWAY: {bet['away_ev']*100:+.1f}%\n\n"

        msg += f"🔢 *PROBABILIDADES (Modelo Poisson):*\n"
        msg += f"   • {bet['home_team']}: {bet['probabilities_model']['home_win']}%\n"
        msg += f"   • Empate: {bet['probabilities_model']['draw']}%\n"
        msg += f"   • {bet['away_team']}: {bet['probabilities_model']['away_win']}%\n\n"

        msg += f"📈 *STATS:*\n"
        home_stats = bet['stats']['home']
        away_stats = bet['stats']['away']
        msg += f"   {bet['home_team']}: ATK {home_stats['attack']} | DEF {home_stats['defense']} | FORM {home_stats['form']}\n"
        msg += f"   {bet['away_team']}: ATK {away_stats['attack']} | DEF {away_stats['defense']} | FORM {away_stats['form']}\n\n"

        msg += f"⚠️ _Apuesta responsablemente_"

        return msg


if __name__ == '__main__':
    """Test del sistema con ejemplos reales"""

    # Fix para emojis en Windows
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

    print("=" * 70)
    print("TEST: ValueBetFinder con datos reales de football-data.org")
    print("=" * 70)

    try:
        finder = ValueBetFinder()

        # Test 1: Analizar un partido específico con odds de ejemplo
        # (Las odds vendrían de una API de odds en producción)
        print("\n1. ANALYZE MATCH - Arsenal vs Liverpool")
        print("-" * 70)

        # Odds de ejemplo (en producción vendrían de The Odds API u otra fuente)
        result = finder.analyze_match(
            home_team="Arsenal",
            away_team="Liverpool",
            home_odds=2.10,  # Arsenal gana
            away_odds=3.40,  # Liverpool gana
            draw_odds=3.60,  # Empate
            competition_id=2021  # Premier League
        )

        if 'error' not in result:
            print(f"\nPartido: {result['home_team']} vs {result['away_team']}")
            print(f"\nRECOMENDACIÓN: {result['recommendation']}")
            print(f"Confianza: {result['confidence']}%")

            print(f"\nMEJOR APUESTA: {result['best_bet']}")
            print(f"  Odds: {result['best_odds']}")
            print(f"  Expected Value: +{result['best_ev']*100:.2f}%")
            print(f"  Probabilidad modelo: {result['best_prob']}%")

            print(f"\nEXPECTED VALUES:")
            print(f"  HOME: {result['home_ev']*100:+.2f}%")
            print(f"  DRAW: {result['draw_ev']*100:+.2f}%")
            print(f"  AWAY: {result['away_ev']*100:+.2f}%")

            print(f"\nPROBABILIDADES MODELO (Poisson):")
            print(f"  {result['home_team']} gana: {result['probabilities_model']['home_win']}%")
            print(f"  Empate: {result['probabilities_model']['draw']}%")
            print(f"  {result['away_team']} gana: {result['probabilities_model']['away_win']}%")

            print(f"\nPROBABILIDADES IMPLÍCITAS (Odds):")
            print(f"  {result['home_team']} gana: {result['probabilities_implied']['home_win']}%")
            print(f"  Empate: {result['probabilities_implied']['draw']}%")
            print(f"  {result['away_team']} gana: {result['probabilities_implied']['away_win']}%")

            print(f"\nSTATS:")
            home_stats = result['stats']['home']
            away_stats = result['stats']['away']
            print(f"  {result['home_team']}: ATK={home_stats['attack']} DEF={home_stats['defense']} FORM={home_stats['form']}")
            print(f"  {result['away_team']}: ATK={away_stats['attack']} DEF={away_stats['defense']} FORM={away_stats['form']}")
            print(f"  Lambdas: λ_home={result['stats']['lambda_home']}, λ_away={result['stats']['lambda_away']}")

            # Test formato Telegram
            print("\n" + "=" * 70)
            print("FORMATO TELEGRAM:")
            print("=" * 70)
            telegram_msg = finder.format_telegram_message(result)
            print(telegram_msg)

        else:
            print(f"Error: {result['error']}")

        # Test 2: Find value in competition
        print("\n" + "=" * 70)
        print("2. FIND VALUE IN COMPETITION - Premier League")
        print("-" * 70)

        value_bets = finder.find_value_in_competition(2021)
        print(f"\nValue bets encontrados: {len(value_bets)}")

        if value_bets:
            print("\n🔥 TOP VALUE BETS:")
            for i, bet in enumerate(value_bets[:3], 1):
                print(f"\n{i}. {bet['home_team']} vs {bet['away_team']}")
                print(f"   Recomendación: {bet['recommendation']}")
                print(f"   Mejor apuesta: {bet['best_bet']} @ {bet['best_odds']}")
                print(f"   Expected Value: +{bet['best_ev']*100:.1f}%")
                print(f"   Confianza: {bet['confidence']}%")
        else:
            print("\nNo se encontraron value bets (o no hay partidos próximos).")

        print("\n" + "=" * 70)
        print("TEST COMPLETADO - OK")
        print("=" * 70)

    except Exception as e:
        print(f"\nERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
