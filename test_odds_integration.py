"""
Test de integración: The Odds API + Value Bets
Demuestra el flujo completo de detección automática de value bets
"""

import sys
import logging
from value_bets import ValueBetFinder

# Fix para emojis en Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_full_flow():
    """Test del flujo completo con odds reales automáticas"""

    print("=" * 80)
    print("TEST: INTEGRACIÓN COMPLETA - The Odds API + Value Bets")
    print("=" * 80)

    finder = ValueBetFinder()

    # Test 1: Analizar una competición completa
    print("\n🔍 BUSCANDO VALUE BETS EN PREMIER LEAGUE...")
    print("-" * 80)

    value_bets = finder.find_value_in_competition(2021)

    print(f"\n📊 RESULTADOS:")
    print(f"Value bets encontrados: {len(value_bets)}")

    if value_bets:
        print("\n🔥 TOP VALUE BETS:\n")

        for i, bet in enumerate(value_bets[:5], 1):
            print(f"{i}. {bet['home_team']} vs {bet['away_team']}")
            print(f"   📅 Fecha: {bet.get('match_date', 'TBD')}")
            print(f"   🎯 Recomendación: {bet['recommendation']}")
            print(f"   💰 Mejor apuesta: {bet['best_bet']} @ {bet['best_odds']}")
            print(f"   📈 Expected Value: +{bet['best_ev']*100:.2f}%")
            print(f"   ⭐ Confianza: {bet['confidence']}%")
            print(f"   🏦 Bookmaker: {bet.get('bookmaker', 'N/A')}")
            print()

            # Mostrar mensaje formateado para Telegram
            if i == 1:
                print("   📱 FORMATO TELEGRAM:")
                print("   " + "-" * 70)
                telegram_msg = finder.format_telegram_message(bet)
                for line in telegram_msg.split('\n'):
                    print(f"   {line}")
                print("   " + "-" * 70)
                print()
    else:
        print("\n⚠️ No se encontraron value bets en este momento.")
        print("\nPosibles razones:")
        print("  • No hay partidos próximos (fuera de temporada)")
        print("  • Las odds actuales no ofrecen value")
        print("  • Se alcanzó el límite de requests de The Odds API")

        if finder.data_fetcher.odds_requests_remaining is not None:
            print(f"\n📊 Requests restantes: {finder.data_fetcher.odds_requests_remaining}")

    print("\n" + "=" * 80)
    print("TEST COMPLETADO")
    print("=" * 80)

    # Información sobre el flujo
    print("\n📝 FLUJO DEL SISTEMA:")
    print("1. find_value_in_competition() obtiene próximos partidos de football-data.org")
    print("2. Para cada partido, get_real_odds() busca odds en The Odds API")
    print("3. Si hay odds, analyze_match() calcula EV con modelo Poisson")
    print("4. Solo retorna partidos con EV > 5%")
    print("5. Se pausa automáticamente si requests_remaining < 50")

    if finder.data_fetcher.odds_requests_remaining:
        print(f"\n✓ API Status: {finder.data_fetcher.odds_requests_remaining} requests disponibles")


if __name__ == '__main__':
    test_full_flow()
