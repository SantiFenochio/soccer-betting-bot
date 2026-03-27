"""
Configuration
Configuración centralizada del bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Base de datos
DB_PATH = os.getenv('DB_PATH', str(DATA_DIR / 'predictions.db'))

# Notificaciones
NOTIFICATION_TIME = os.getenv('NOTIFICATION_TIME', '09:00')
NOTIFICATION_TIMEZONE = os.getenv('NOTIFICATION_TIMEZONE', 'America/Argentina/Buenos_Aires')

# Análisis
MIN_CONFIDENCE = int(os.getenv('MIN_CONFIDENCE', '70'))
MIN_MATCHES_ANALYSIS = 10  # Mínimo de partidos para análisis confiable

# Ligas soportadas
SUPPORTED_LEAGUES = {
    'ESP': {
        'name': 'La Liga',
        'country': 'España',
        'flag': '🇪🇸',
        'fbref_code': 'ESP',
        'understat_code': 'La Liga'
    },
    'ENG': {
        'name': 'Premier League',
        'country': 'Inglaterra',
        'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'fbref_code': 'ENG',
        'understat_code': 'EPL'
    },
    'GER': {
        'name': 'Bundesliga',
        'country': 'Alemania',
        'flag': '🇩🇪',
        'fbref_code': 'GER',
        'understat_code': 'Bundesliga'
    },
    'ITA': {
        'name': 'Serie A',
        'country': 'Italia',
        'flag': '🇮🇹',
        'fbref_code': 'ITA',
        'understat_code': 'Serie A'
    },
    'FRA': {
        'name': 'Ligue 1',
        'country': 'Francia',
        'flag': '🇫🇷',
        'fbref_code': 'FRA',
        'understat_code': 'Ligue 1'
    },
    'ARG': {
        'name': 'Liga Profesional',
        'country': 'Argentina',
        'flag': '🇦🇷',
        'fbref_code': 'ARG',
        'understat_code': None  # No disponible en Understat
    }
}

# Umbrales de confianza
CONFIDENCE_THRESHOLDS = {
    'high': 80,      # 🔥
    'medium': 70,    # ✅
    'low': 60        # ⚠️
}

# Rate limiting
API_RATE_LIMIT_DELAY = 0.5  # segundos entre requests

# Cache
CACHE_EXPIRY_HOURS = 24

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Features flags
ENABLE_NOTIFICATIONS = True
ENABLE_PRE_MATCH_ALERTS = False  # Futuro
ENABLE_LIVE_TRACKING = False      # Futuro

# Disclaimers
DISCLAIMER_TEXT = """
⚠️ *DISCLAIMER*

Este bot proporciona análisis estadístico con fines educativos.
Las predicciones NO son garantías de resultado.

🎲 Las apuestas pueden causar adicción.
💰 No apuestes más de lo que puedas permitirte perder.
🧠 Juega responsablemente.

Consulta recursos de ayuda si tienes problemas con las apuestas.
"""


def validate_config() -> bool:
    """Validar configuración"""
    errors = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN no configurado")

    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if errors:
        print("❌ Errores de configuración:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True


if __name__ == '__main__':
    print("🔧 Configuración del Bot\n")

    if validate_config():
        print("✅ Configuración válida")
        print(f"\n📊 Configuración actual:")
        print(f"  - Token configurado: {'Sí' if TELEGRAM_BOT_TOKEN else 'No'}")
        print(f"  - Chat ID: {TELEGRAM_CHAT_ID or 'No configurado'}")
        print(f"  - Hora de notificaciones: {NOTIFICATION_TIME}")
        print(f"  - Confianza mínima: {MIN_CONFIDENCE}%")
        print(f"  - Ligas: {len(SUPPORTED_LEAGUES)}")
    else:
        print("❌ Configuración inválida")
