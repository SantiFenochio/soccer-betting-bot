"""
Test rápido del bot sin iniciarlo
Verifica que todas las dependencias estén correctas
"""

import sys
import os

# Fix encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 70)
print("TEST: Soccer Betting Bot")
print("=" * 70)

# 1. Test imports
print("\n1. VERIFICANDO IMPORTS...")
print("-" * 70)

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes
    print("✓ python-telegram-bot importado correctamente")
except ImportError as e:
    print(f"✗ Error importando python-telegram-bot: {e}")
    sys.exit(1)

try:
    from value_bets import ValueBetFinder
    print("✓ ValueBetFinder importado correctamente")
except ImportError as e:
    print(f"✗ Error importando ValueBetFinder: {e}")
    sys.exit(1)

try:
    from data_fetcher import DataFetcher
    print("✓ DataFetcher importado correctamente")
except ImportError as e:
    print(f"✗ Error importando DataFetcher: {e}")
    sys.exit(1)

try:
    from bot import SoccerBettingBot, LEAGUES
    print("✓ SoccerBettingBot importado correctamente")
except ImportError as e:
    print(f"✗ Error importando SoccerBettingBot: {e}")
    sys.exit(1)

# 2. Test variables de entorno
print("\n2. VERIFICANDO VARIABLES DE ENTORNO...")
print("-" * 70)

from dotenv import load_dotenv
load_dotenv()

telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
football_key = os.getenv('FOOTBALL_DATA_KEY')
odds_key = os.getenv('ODDS_API_KEY')

if telegram_token:
    print(f"✓ TELEGRAM_BOT_TOKEN: {telegram_token[:20]}...")
else:
    print("✗ TELEGRAM_BOT_TOKEN no encontrada")

if football_key:
    print(f"✓ FOOTBALL_DATA_KEY: {football_key[:20]}...")
else:
    print("✗ FOOTBALL_DATA_KEY no encontrada")

if odds_key:
    print(f"✓ ODDS_API_KEY: {odds_key[:20]}...")
else:
    print("✗ ODDS_API_KEY no encontrada")

# 3. Test inicialización del bot
print("\n3. VERIFICANDO INICIALIZACIÓN DEL BOT...")
print("-" * 70)

if not telegram_token:
    print("⚠️ No se puede inicializar bot sin TELEGRAM_BOT_TOKEN")
else:
    try:
        bot = SoccerBettingBot(telegram_token)
        print("✓ SoccerBettingBot inicializado correctamente")
        print(f"✓ ValueFinder: {type(bot.value_finder).__name__}")
        print(f"✓ DataFetcher: {type(bot.data_fetcher).__name__}")
    except Exception as e:
        print(f"✗ Error inicializando bot: {e}")
        import traceback
        traceback.print_exc()

# 4. Test ligas configuradas
print("\n4. VERIFICANDO LIGAS CONFIGURADAS...")
print("-" * 70)

for code, info in LEAGUES.items():
    print(f"✓ {code}: {info['name']} (ID: {info['id']})")

# 5. Test comandos disponibles
print("\n5. COMANDOS DEL BOT...")
print("-" * 70)

commands = [
    ("/start", "Mensaje de bienvenida"),
    ("/ayuda", "Guía de comandos"),
    ("/analizar [liga]", "Buscar value bets"),
    ("/partidos [liga]", "Próximos partidos"),
    ("/estado", "Estado de APIs")
]

for cmd, desc in commands:
    print(f"• {cmd:20} → {desc}")

# Resumen
print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)

issues = []

if not telegram_token:
    issues.append("TELEGRAM_BOT_TOKEN faltante")
if not football_key:
    issues.append("FOOTBALL_DATA_KEY faltante")
if not odds_key:
    issues.append("ODDS_API_KEY faltante")

if issues:
    print("\n⚠️ PROBLEMAS ENCONTRADOS:")
    for issue in issues:
        print(f"   • {issue}")
    print("\nConfigura las variables en .env antes de iniciar el bot.")
else:
    print("\n✓ TODO LISTO")
    print("\nPara iniciar el bot:")
    print("   python bot.py")
    print("\nO usa:")
    print("   run.bat      (Windows)")
    print("   ./run.sh     (Linux/Mac)")

print("\n" + "=" * 70)
