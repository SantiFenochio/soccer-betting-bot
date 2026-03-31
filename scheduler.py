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
from database import Database
from data_fetcher import DataFetcher

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
        self.db = Database()
        self.data_fetcher = DataFetcher()
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

    async def verify_yesterday_predictions(self):
        """
        Verificar resultados de predicciones del día anterior

        Se ejecuta diariamente a las 23:00 (America/Argentina/Buenos_Aires)
        """
        logger.info("🔍 Verificando predicciones del día anterior...")

        try:
            # Obtener fecha de ayer
            yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

            # Obtener predicciones sin verificar de ayer
            unverified = self.db.get_unverified_predictions(yesterday)

            if not unverified:
                logger.info(f"No hay predicciones sin verificar para {yesterday}")
                return

            logger.info(f"Encontradas {len(unverified)} predicciones para verificar")

            verified_count = 0
            correct_count = 0

            for pred in unverified:
                try:
                    # Obtener resultado real del partido
                    result = self.data_fetcher.get_match_result(
                        pred['home_team'],
                        pred['away_team'],
                        pred['date']
                    )

                    if not result or result['status'] != 'finished':
                        logger.debug(f"Resultado no disponible para {pred['home_team']} vs {pred['away_team']}")
                        continue

                    home_score = result['home_score']
                    away_score = result['away_score']
                    actual_score = result['score']

                    # Verificar si la predicción fue correcta
                    is_correct = self._check_prediction_correct(
                        pred['prediction_type'],
                        home_score,
                        away_score
                    )

                    # Actualizar en base de datos
                    success = self.db.update_prediction_result(
                        pred['id'],
                        is_correct,
                        actual_score
                    )

                    if success:
                        verified_count += 1
                        if is_correct:
                            correct_count += 1

                        logger.info(
                            f"✓ {pred['home_team']} vs {pred['away_team']}: "
                            f"{actual_score} - {'CORRECTO' if is_correct else 'INCORRECTO'}"
                        )

                except Exception as e:
                    logger.error(f"Error verificando predicción {pred['id']}: {e}")
                    continue

            logger.info(
                f"✅ Verificación completada: {verified_count} verificadas, "
                f"{correct_count} correctas ({(correct_count/verified_count*100):.1f}% accuracy)"
            )

        except Exception as e:
            logger.error(f"Error en verificación de predicciones: {e}")

    def _check_prediction_correct(self, prediction_type: str, home_score: int, away_score: int) -> bool:
        """
        Verificar si una predicción fue correcta según el resultado real

        Args:
            prediction_type: Tipo de predicción (ej: "🏆 Ganador", "⚽ Goles", etc.)
            home_score: Goles del equipo local
            away_score: Goles del equipo visitante

        Returns:
            bool: True si la predicción fue correcta
        """
        total_goals = home_score + away_score

        # Normalizar tipo de predicción (quitar emojis y minúsculas)
        pred_lower = prediction_type.lower()

        # Resultado del partido
        if '🏆' in prediction_type or 'ganador' in pred_lower:
            # Verificar según texto de la predicción
            if home_score > away_score:
                return 'gana' in pred_lower or 'victoria' in pred_lower or '1' in pred_lower
            elif away_score > home_score:
                return 'gana' in pred_lower or 'victoria' in pred_lower or '2' in pred_lower
            else:
                return 'empate' in pred_lower or 'draw' in pred_lower

        # Over/Under 2.5 goles
        elif '⚽' in prediction_type or 'goles' in pred_lower:
            if 'over' in pred_lower:
                return total_goals > 2.5
            elif 'under' in pred_lower:
                return total_goals < 2.5

        # Ambos anotan (BTTS)
        elif '🎯' in prediction_type or 'ambos' in pred_lower or 'btts' in pred_lower:
            both_scored = home_score > 0 and away_score > 0
            if 'sí' in pred_lower or 'yes' in pred_lower:
                return both_scored
            elif 'no' in pred_lower:
                return not both_scored

        # Por defecto, no podemos verificar
        logger.warning(f"No se puede verificar tipo de predicción: {prediction_type}")
        return False

    async def retrain_ml_model(self):
        """
        Reentrenar modelo ML con datos actualizados

        Se ejecuta semanalmente (domingos a las 22:00)
        """
        logger.info("🤖 Iniciando reentrenamiento de modelo ML...")

        try:
            from ml_model import MLPredictor

            predictor = MLPredictor()

            # Entrenar con datos de últimas 4 temporadas
            success = predictor.train_model(seasons=4)

            if success:
                logger.info("✅ Modelo ML reentrenado exitosamente")

                # Notificar a admins (opcional)
                admin_message = """
🤖 *MODELO ML ACTUALIZADO*

El modelo de Machine Learning ha sido reentrenado exitosamente con datos actualizados.

✅ Las predicciones ahora usan el modelo más reciente.

📊 _Entrenado con datos de las últimas 4 temporadas_
                """

                # Enviar solo si hay chat_id configurado
                chat_id = os.getenv('TELEGRAM_CHAT_ID')
                if chat_id:
                    try:
                        await self.bot.send_message(
                            chat_id=int(chat_id),
                            text=admin_message,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception as e:
                        logger.warning(f"No se pudo enviar notificación de reentrenamiento: {e}")
            else:
                logger.error("❌ Error en reentrenamiento de modelo ML")

        except Exception as e:
            logger.error(f"Error en reentrenamiento ML: {e}")

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

        # Verificación de resultados (diario a las 23:00 Argentina)
        schedule.every().day.at("23:00").do(
            lambda: asyncio.run(self.verify_yesterday_predictions())
        )

        # Resumen semanal (domingos)
        schedule.every().sunday.at("20:00").do(
            lambda: asyncio.run(self.send_weekly_summary())
        )

        # Reentrenamiento ML (domingos a las 22:00)
        schedule.every().sunday.at("22:00").do(
            lambda: asyncio.run(self.retrain_ml_model())
        )

        logger.info(f"✅ Jobs programados:")
        logger.info(f"  - Predicciones diarias: {notification_time}")
        logger.info(f"  - Verificación de resultados: 23:00 (diario)")
        logger.info(f"  - Resumen semanal: Domingos 20:00")
        logger.info(f"  - Reentrenamiento ML: Domingos 22:00")

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
