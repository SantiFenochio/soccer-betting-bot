"""
Main Entry Point
Punto de entrada principal del bot
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def setup_directories():
    """Crear directorios necesarios"""
    dirs = ['data', 'logs']

    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)

    logger.info("✓ Directorios configurados")


def check_environment():
    """Verificar variables de entorno"""
    load_dotenv()

    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN no encontrado en .env")
        logger.error("Por favor, configura tu token en el archivo .env")
        return False

    logger.info("✓ Variables de entorno cargadas")
    return True


def install_dependencies():
    """Verificar e instalar dependencias si es necesario"""
    try:
        import telegram
        import pandas
        import soccerdata
        logger.info("✓ Dependencias verificadas")
        return True

    except ImportError as e:
        logger.warning(f"⚠️  Dependencia faltante: {e}")
        logger.info("📦 Instalando dependencias...")

        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info("✓ Dependencias instaladas correctamente")
            return True
        else:
            logger.error(f"❌ Error instalando dependencias: {result.stderr}")
            return False


def main():
    """Función principal"""
    print("=" * 50)
    print("⚽ SOCCER BETTING BOT")
    print("=" * 50)
    print()

    # 1. Configurar directorios
    logger.info("🔧 Configurando entorno...")
    setup_directories()

    # 2. Verificar variables de entorno
    if not check_environment():
        sys.exit(1)

    # 3. Verificar dependencias
    if not install_dependencies():
        logger.error("❌ No se pudieron instalar las dependencias")
        sys.exit(1)

    # 4. Seleccionar modo
    print("\n¿Qué deseas ejecutar?")
    print("1. Bot de Telegram (interactivo)")
    print("2. Scheduler (notificaciones automáticas)")
    print("3. Ambos (recomendado)")
    print("4. Test de conexión")
    print()

    mode = input("Selecciona una opción (1-4): ").strip()

    if mode == '1':
        logger.info("🤖 Iniciando Bot de Telegram...")
        from bot import SoccerBettingBot

        token = os.getenv('TELEGRAM_BOT_TOKEN')
        bot = SoccerBettingBot(token)
        bot.run()

    elif mode == '2':
        logger.info("⏰ Iniciando Scheduler...")
        from scheduler import NotificationScheduler

        token = os.getenv('TELEGRAM_BOT_TOKEN')
        scheduler = NotificationScheduler(token)
        scheduler.run()

    elif mode == '3':
        logger.info("🚀 Iniciando Bot + Scheduler...")
        import threading
        from bot import SoccerBettingBot
        from scheduler import NotificationScheduler

        token = os.getenv('TELEGRAM_BOT_TOKEN')

        # Iniciar scheduler en thread separado
        scheduler = NotificationScheduler(token)
        scheduler_thread = threading.Thread(target=scheduler.run, daemon=True)
        scheduler_thread.start()

        logger.info("✓ Scheduler iniciado en background")

        # Iniciar bot en thread principal
        bot = SoccerBettingBot(token)
        bot.run()

    elif mode == '4':
        logger.info("🧪 Ejecutando test de conexión...")
        import asyncio
        from scheduler import test_notification

        asyncio.run(test_notification())

    else:
        logger.error("❌ Opción inválida")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot detenido por el usuario")
        logger.info("Bot detenido")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
