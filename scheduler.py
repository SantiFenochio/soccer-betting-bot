"""
Scheduler
Sistema de notificaciones automáticas

⚠️ NOTA: Este módulo está parcialmente deshabilitado en la versión simplificada del bot.
La versión simplificada se enfoca en comandos manuales (/fijini, /hoy) sin sistema de
notificaciones automáticas. Para habilitar, se requiere reinstalar database.py y
configurar manualmente los chat IDs de usuarios suscritos.
"""

import os
import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import List
import logging

from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

from analyzer import SoccerAnalyzer
# from database import DatabaseManager  # DESHABILITADO - Ver versión simplificada

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Gestor de notificaciones automáticas

    NOTA: Este módulo está parcialmente deshabilitado en la versión simplificada.
    Las notificaciones requieren configuración manual de chat IDs.
    """

    def __init__(self, bot_token: str):
        """Inicializar scheduler"""
        self.bot = Bot(token=bot_token)
        self.analyzer = SoccerAnalyzer()
        # self.db = DatabaseManager()  # DESHABILITADO
        self.min_confidence = int(os.getenv('MIN_CONFIDENCE', '70'))

    async def send_daily_predictions(self):
        """Enviar predicciones diarias a usuarios suscritos"""
        logger.info("📨 Enviando predicciones diarias...")

        try:
            # Obtener partidos del día
            matches = self.analyzer.get_today_matches()

            if not matches:
                logger.info("No hay partidos para hoy")
                return

            # Filtrar mejores predicciones
            top_predictions = []

            for match in matches:
                if match['predictions']:
                    # Tomar la mejor predicción de cada partido
                    best_pred = match['predictions'][0]

                    if best_pred['confidence'] >= self.min_confidence:
                        top_predictions.append({
                            'match': match,
                            'prediction': best_pred
                        })

            if not top_predictions:
                logger.info("No hay predicciones con suficiente confianza")
                return

            # Ordenar por confianza
            top_predictions.sort(
                key=lambda x: x['prediction']['confidence'],
                reverse=True
            )

            # Crear mensaje
            message = self._format_daily_message(top_predictions[:5])  # Top 5

            # Enviar a usuarios suscritos
            users = self.db.get_subscribed_users()
            sent_count = 0

            for chat_id in users:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    sent_count += 1
                    await asyncio.sleep(0.5)  # Evitar rate limit

                except Exception as e:
                    logger.error(f"Error enviando a {chat_id}: {e}")

            logger.info(f"✅ Notificaciones enviadas a {sent_count} usuarios")

            # Guardar predicciones en DB
            for item in top_predictions:
                match = item['match']
                pred = item['prediction']

                self.db.save_prediction({
                    'date': datetime.now().date().isoformat(),
                    'league': match['league'],
                    'home_team': match['home'],
                    'away_team': match['away'],
                    'type': pred['type'],
                    'confidence': pred['confidence'],
                    'description': pred['description'],
                    'reason': pred['reason']
                })

        except Exception as e:
            logger.error(f"Error en notificaciones diarias: {e}")

    def _format_daily_message(self, predictions: List[dict]) -> str:
        """Formatear mensaje diario"""
        today = datetime.now().strftime("%d/%m/%Y")

        message = f"🔥 *PREDICCIONES DEL DÍA* 🔥\n"
        message += f"📅 {today}\n\n"
        message += f"Top {len(predictions)} apuestas con mayor confianza:\n\n"

        for i, item in enumerate(predictions, 1):
            match = item['match']
            pred = item['prediction']

            conf_emoji = "🔥" if pred['confidence'] >= 85 else "✅" if pred['confidence'] >= 75 else "⚠️"

            message += f"{i}. {conf_emoji} *{match['home']} vs {match['away']}*\n"
            message += f"   🏆 {match['league']}\n"
            message += f"   🕐 {match.get('time', 'TBD')}\n\n"
            message += f"   🎯 *{pred['type']}*\n"
            message += f"   📊 Confianza: *{pred['confidence']}%*\n"
            message += f"   💡 {pred['description']}\n"
            message += f"   📝 _{pred['reason']}_\n\n"

        message += "━━━━━━━━━━━━━━━━━━━━\n"
        message += "⚠️ *Recuerda:* Apuesta responsablemente\n"
        message += "💬 Usa /partido para análisis detallado\n"

        return message

    async def send_pre_match_notification(self, match_info: dict):
        """
        Enviar notificación 1-2 horas antes de un partido importante

        Args:
            match_info: Información del partido
        """
        try:
            message = f"⏰ *RECORDATORIO DE PARTIDO*\n\n"
            message += f"🏠 {match_info['home']} vs {match_info['away']} 🚗\n"
            message += f"🏆 {match_info['league']}\n"
            message += f"🕐 Comienza en {match_info['minutes_until']} minutos\n\n"

            if 'prediction' in match_info:
                pred = match_info['prediction']
                message += f"🎯 *Predicción: {pred['type']}*\n"
                message += f"📊 Confianza: {pred['confidence']}%\n"
                message += f"💡 {pred['description']}\n"

            users = self.db.get_subscribed_users()

            for chat_id in users:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error enviando notificación pre-partido: {e}")

        except Exception as e:
            logger.error(f"Error en notificación pre-partido: {e}")

    async def send_weekly_summary(self):
        """Enviar resumen semanal de resultados"""
        logger.info("📊 Enviando resumen semanal...")

        try:
            stats = self.db.get_statistics(7)

            if stats['verified_predictions'] == 0:
                logger.info("No hay datos suficientes para resumen semanal")
                return

            message = f"📊 *RESUMEN SEMANAL*\n\n"
            message += f"📅 Última semana:\n\n"

            message += f"📈 Predicciones realizadas: {stats['total_predictions']}\n"
            message += f"✅ Verificadas: {stats['verified_predictions']}\n"
            message += f"🎯 Correctas: {stats['correct_predictions']}\n"
            message += f"📊 Precisión: *{stats['accuracy']}%*\n\n"

            if stats['by_type']:
                message += "🎲 *Precisión por tipo:*\n"
                for pred_type, data in sorted(
                    stats['by_type'].items(),
                    key=lambda x: x[1]['accuracy'],
                    reverse=True
                ):
                    emoji = "🔥" if data['accuracy'] >= 75 else "✅" if data['accuracy'] >= 65 else "⚠️"
                    message += f"{emoji} {pred_type}: {data['accuracy']}%\n"

            message += "\n━━━━━━━━━━━━━━━━━━━━\n"
            message += "💡 Seguimos mejorando para darte las mejores predicciones!\n"

            users = self.db.get_subscribed_users()

            for chat_id in users:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error enviando resumen: {e}")

            logger.info("✅ Resumen semanal enviado")

        except Exception as e:
            logger.error(f"Error en resumen semanal: {e}")

    def schedule_jobs(self):
        """Programar trabajos automáticos"""
        notification_time = os.getenv('NOTIFICATION_TIME', '09:00')

        # Predicciones diarias
        schedule.every().day.at(notification_time).do(
            lambda: asyncio.run(self.send_daily_predictions())
        )

        # Resumen semanal (domingos)
        schedule.every().sunday.at("20:00").do(
            lambda: asyncio.run(self.send_weekly_summary())
        )

        logger.info(f"✅ Jobs programados:")
        logger.info(f"  - Predicciones diarias: {notification_time}")
        logger.info(f"  - Resumen semanal: Domingos 20:00")

    def run(self):
        """Ejecutar scheduler"""
        logger.info("⏰ Iniciando Notification Scheduler...")

        self.schedule_jobs()

        logger.info("✅ Scheduler activo. Esperando eventos...")

        # Loop principal
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto

            except KeyboardInterrupt:
                logger.info("⏹️  Scheduler detenido")
                break
            except Exception as e:
                logger.error(f"Error en scheduler: {e}")
                time.sleep(60)


async def test_notification():
    """Test de notificaciones"""
    load_dotenv()

    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    if not TOKEN or not CHAT_ID:
        print("❌ Faltan variables de entorno")
        return

    scheduler = NotificationScheduler(TOKEN)

    # Test: Enviar predicción de prueba
    print("📨 Enviando notificación de prueba...")

    test_message = """
🔥 *TEST DE NOTIFICACIÓN* 🔥

✅ Si ves este mensaje, las notificaciones funcionan correctamente!

El bot te enviará predicciones diarias automáticamente.

💬 Usa /help para ver todos los comandos disponibles.
    """

    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(
            chat_id=int(CHAT_ID),
            text=test_message,
            parse_mode=ParseMode.MARKDOWN
        )
        print("✅ Notificación enviada exitosamente!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Modo test
        asyncio.run(test_notification())
    else:
        # Modo normal
        load_dotenv()
        TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

        if not TOKEN:
            print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado en .env")
            exit(1)

        scheduler = NotificationScheduler(TOKEN)
        scheduler.run()
