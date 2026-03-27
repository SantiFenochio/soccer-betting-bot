"""
Telegram Bot
Bot de Telegram para predicciones de fútbol
"""

import os
import logging
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode

from analyzer import SoccerAnalyzer, format_prediction
from database import DatabaseManager

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('./logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SoccerBettingBot:
    """Bot de Telegram para análisis de fútbol"""

    def __init__(self, token: str):
        """Inicializar bot"""
        self.token = token
        self.analyzer = SoccerAnalyzer()
        self.db = DatabaseManager()
        self.app = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id

        # Guardar usuario en DB
        self.db.save_user(chat_id, {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'subscribed': True
        })

        welcome_message = f"""
⚽ *¡Bienvenido al Bot de Análisis de Fútbol!* ⚽

Hola {user.first_name}! 👋

Este bot analiza datos de las principales ligas de fútbol y te envía predicciones basadas en estadísticas reales.

🎯 *Tu Chat ID:* `{chat_id}`

📊 *Ligas disponibles:*
🇪🇸 La Liga
🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
🇩🇪 Bundesliga
🇮🇹 Serie A
🇫🇷 Ligue 1
🇦🇷 Liga Profesional Argentina

💬 *Comandos disponibles:*
/hoy - Partidos y predicciones de hoy
/proximos [días] - Partidos de los próximos días (default: 7)
/analizar [equipo] - Análisis de un equipo
/partido [local] vs [visitante] - Predicción específica
/selecciones [país1] vs [país2] - Predicción de selecciones
/tendencias - Patrones más confiables
/stats - Ver estadísticas del bot
/ligas - Ver todas las ligas
/mundial - Info sobre Copa del Mundo 2026
/suscribir - Activar/desactivar notificaciones
/help - Ver ayuda

⚠️ *Disclaimer:*
Las predicciones se basan en análisis estadístico.
Ninguna predicción es 100% segura.
Apuesta responsablemente. 🎲

¡Empezá con /hoy para ver los partidos de hoy! 🔥
        """

        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = """
📖 *Guía de Comandos*

🎯 *Análisis de partidos:*
/hoy - Partidos de hoy con predicciones
/proximos 3 - Partidos de los próximos 3 días
/partido Manchester City vs Liverpool - Predicción de partido
/analizar Real Madrid - Stats del equipo
/selecciones Argentina vs Brasil - Predicción de selecciones

📊 *Información:*
/tendencias - Patrones estadísticos confiables
/stats - Estadísticas del bot (precisión)
/ligas - Ver todas las ligas disponibles

⚙️ *Configuración:*
/suscribir - Activar/desactivar notificaciones diarias

💡 *Ejemplos:*
• `/partido Barcelona vs Real Madrid`
• `/analizar Manchester City`
• `/hoy` para ver todos los partidos de hoy

⚠️ Recuerda apostar responsablemente!
        """

        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /hoy - Partidos de hoy"""
        await update.message.reply_text("🔍 Buscando partidos de hoy...")

        try:
            matches = self.analyzer.get_today_matches()

            if not matches:
                await update.message.reply_text(
                    "😔 No hay partidos programados para hoy en las ligas principales."
                )
                return

            response = "⚽ *PARTIDOS DE HOY*\n\n"

            for match in matches[:10]:  # Máximo 10 partidos
                response += f"🏆 *{match['league']}*\n"
                response += f"🏠 {match['home']} vs {match['away']} 🚗\n"
                response += f"🕐 Hora: {match['time']}\n"

                if match['predictions']:
                    best_pred = match['predictions'][0]  # Mejor predicción
                    conf_emoji = "🔥" if best_pred['confidence'] >= 80 else "✅"

                    response += f"{conf_emoji} *{best_pred['type']}* ({best_pred['confidence']}%)\n"
                    response += f"└ _{best_pred['description']}_\n\n"
                else:
                    response += "⚠️ Sin predicciones confiables\n\n"

            response += "\n💡 Usa /partido [equipo1] vs [equipo2] para análisis detallado"

            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error en /hoy: {e}")
            await update.message.reply_text(
                "❌ Error al obtener partidos. Intenta de nuevo."
            )

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analizar [equipo]"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: /analizar [nombre del equipo]\n"
                "Ejemplo: `/analizar Manchester City`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        team_name = ' '.join(context.args)
        await update.message.reply_text(f"🔍 Analizando {team_name}...")

        try:
            # Por defecto buscar en Premier League, expandir si no se encuentra
            stats = self.analyzer.get_team_stats(team_name, 'ENG', n_matches=10)

            if 'error' in stats:
                await update.message.reply_text(
                    f"❌ No se encontraron datos para {team_name}\n"
                    "Verifica el nombre del equipo."
                )
                return

            response = f"📊 *Análisis de {stats['team']}*\n\n"
            response += f"📈 *Últimos {stats['matches_analyzed']} partidos:*\n\n"

            response += f"🎯 *Resultados:*\n"
            response += f"✅ Victorias: {stats['wins']}\n"
            response += f"➖ Empates: {stats['draws']}\n"
            response += f"❌ Derrotas: {stats['losses']}\n\n"

            response += f"⚽ *Goles:*\n"
            response += f"📤 Promedio anotados: {stats.get('avg_goals_scored', 0)}\n"
            response += f"📥 Promedio recibidos: {stats.get('avg_goals_conceded', 0)}\n"
            response += f"🧤 Valla invicta: {stats.get('clean_sheet_percentage', 0)}%\n\n"

            response += f"📊 *Tendencias:*\n"
            response += f"🎲 BTTS: {stats.get('btts_percentage', 0)}%\n"
            response += f"🔺 Over 2.5: {stats.get('over_25_percentage', 0)}%\n"
            response += f"🔻 Over 3.5: {stats.get('over_35_percentage', 0)}%\n\n"

            # Recomendación
            if stats.get('over_25_percentage', 0) > 70:
                response += "💡 *Recomendación:* Bueno para Over 2.5 goles\n"
            elif stats.get('btts_percentage', 0) > 70:
                response += "💡 *Recomendación:* Muy probable BTTS\n"
            elif stats.get('clean_sheet_percentage', 0) > 50:
                response += "💡 *Recomendación:* Defensa sólida, considerar Under\n"

            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error en /analizar: {e}")
            await update.message.reply_text(
                "❌ Error al analizar equipo. Intenta de nuevo."
            )

    async def match_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /partido [equipo1] vs [equipo2]"""
        if not context.args or 'vs' not in ' '.join(context.args).lower():
            await update.message.reply_text(
                "❌ Uso: /partido [equipo local] vs [equipo visitante]\n"
                "Ejemplo: `/partido Manchester City vs Liverpool`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        full_text = ' '.join(context.args)
        teams = full_text.split(' vs ')

        if len(teams) != 2:
            teams = full_text.split(' VS ')

        if len(teams) != 2:
            await update.message.reply_text(
                "❌ Formato incorrecto. Usa: /partido [equipo1] vs [equipo2]"
            )
            return

        home_team = teams[0].strip()
        away_team = teams[1].strip()

        await update.message.reply_text(
            f"🔍 Analizando {home_team} vs {away_team}..."
        )

        try:
            prediction = self.analyzer.predict_match(home_team, away_team, 'ENG')

            if 'error' in prediction:
                await update.message.reply_text(
                    f"❌ {prediction['error']}\n"
                    "Verifica los nombres de los equipos."
                )
                return

            # Formatear y enviar predicción
            formatted = format_prediction(prediction)
            await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN)

            # Guardar predicciones en DB
            if 'predictions' in prediction:
                for pred in prediction['predictions']:
                    self.db.save_prediction({
                        'date': datetime.now().date().isoformat(),
                        'league': 'Premier League',  # TODO: detectar liga
                        'home_team': home_team,
                        'away_team': away_team,
                        **pred
                    })

        except Exception as e:
            logger.error(f"Error en /partido: {e}")
            await update.message.reply_text(
                "❌ Error al predecir partido. Intenta de nuevo."
            )

    async def trends_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /tendencias - Patrones confiables"""
        patterns = self.analyzer.get_trending_patterns(min_confidence=70)

        response = "📈 *PATRONES MÁS CONFIABLES*\n\n"
        response += "Estos patrones se cumplen con alta frecuencia:\n\n"

        for i, pattern in enumerate(patterns, 1):
            conf_emoji = "🔥" if pattern['confidence'] >= 80 else "✅"

            response += f"{conf_emoji} *{pattern['pattern']}* ({pattern['confidence']}%)\n"
            response += f"└ {pattern['description']}\n"
            response += f"└ _Aplica a: {', '.join(pattern['applies_to'])}_\n\n"

        response += "\n💡 Usa estos patrones como guía para tus análisis!"

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /stats - Estadísticas del bot"""
        stats = self.db.get_statistics(30)

        response = "📊 *ESTADÍSTICAS DEL BOT*\n\n"
        response += f"📅 *Últimos 30 días:*\n\n"

        response += f"📈 Predicciones totales: {stats['total_predictions']}\n"
        response += f"✅ Verificadas: {stats['verified_predictions']}\n"
        response += f"🎯 Correctas: {stats['correct_predictions']}\n"
        response += f"📊 Precisión: *{stats['accuracy']}%*\n\n"

        if stats['by_type']:
            response += "🎲 *Por tipo de predicción:*\n"
            for pred_type, data in stats['by_type'].items():
                response += f"\n• {pred_type}\n"
                response += f"  └ {data['correct']}/{data['total']} ({data['accuracy']}%)\n"

        response += "\n💡 Seguimos mejorando nuestras predicciones!"

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    async def leagues_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ligas"""
        response = "🏆 *LIGAS DISPONIBLES*\n\n"

        for code, name in self.analyzer.LEAGUES.items():
            flag = {
                'ESP': '🇪🇸',
                'ENG': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
                'GER': '🇩🇪',
                'ITA': '🇮🇹',
                'FRA': '🇫🇷',
                'ARG': '🇦🇷'
            }.get(code, '⚽')

            response += f"{flag} *{name}*\n"

        response += "\n💡 Usa /hoy para ver partidos de todas las ligas"

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    async def international_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /selecciones [país1] vs [país2]"""
        if not context.args or 'vs' not in ' '.join(context.args).lower():
            # Mostrar selecciones disponibles
            response = "🌍 *SELECCIONES DISPONIBLES*\n\n"
            response += "🏆 *Sudamérica:*\n"
            response += "🇦🇷 Argentina, 🇧🇷 Brasil, 🇺🇾 Uruguay\n"
            response += "🇨🇴 Colombia, 🇨🇱 Chile, 🇪🇨 Ecuador\n\n"

            response += "🏆 *Europa:*\n"
            response += "🇫🇷 Francia, 🇪🇸 España, 🇩🇪 Alemania\n"
            response += "🇮🇹 Italia, 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra, 🇵🇹 Portugal\n\n"

            response += "💡 *Uso:* `/selecciones Argentina vs Brasil`\n"
            response += "📅 Incluye: Amistosos, Eliminatorias, Mundial 2026"

            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            return

        full_text = ' '.join(context.args)
        teams = full_text.split(' vs ')

        if len(teams) != 2:
            teams = full_text.split(' VS ')

        if len(teams) != 2:
            await update.message.reply_text(
                "❌ Formato incorrecto. Usa: /selecciones [país1] vs [país2]\n"
                "Ejemplo: `/selecciones Argentina vs Brasil`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        team1 = teams[0].strip()
        team2 = teams[1].strip()

        await update.message.reply_text(
            f"🌍 Analizando {team1} vs {team2}..."
        )

        try:
            # Detectar tipo de competición (por defecto amistoso)
            competition = 'FRIENDLIES'
            comp_keywords = {
                'mundial': 'WORLD_CUP',
                'copa america': 'COPA_AMERICA',
                'euro': 'EURO',
                'eliminatoria': 'QUALIFIERS_CONMEBOL',
                'amistoso': 'FRIENDLIES'
            }

            for keyword, comp in comp_keywords.items():
                if keyword in full_text.lower():
                    competition = comp
                    break

            prediction = self.analyzer.predict_international_match(team1, team2, competition)

            if 'error' in prediction:
                await update.message.reply_text(
                    f"❌ {prediction['error']}\n"
                    "Verifica los nombres de las selecciones."
                )
                return

            # Formatear respuesta
            response = f"🌍 *{prediction['match']}*\n"
            response += f"🏆 {prediction['competition']}\n\n"

            if prediction['predictions']:
                response += "📊 *Predicciones:*\n\n"

                for pred in prediction['predictions']:
                    conf_emoji = "🔥" if pred['confidence'] >= 75 else "✅" if pred['confidence'] >= 65 else "⚠️"
                    response += f"{conf_emoji} *{pred['type']}* ({pred['confidence']}%)\n"
                    response += f"   └ {pred['description']}\n"
                    response += f"   └ _{pred['reason']}_\n\n"

            if 'note' in prediction:
                response += f"\n{prediction['note']}"

            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error en /selecciones: {e}")
            await update.message.reply_text(
                "❌ Error al analizar partido de selecciones. Intenta de nuevo."
            )

    async def worldcup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /mundial - Info sobre Mundial 2026"""
        response = """
🏆 *COPA DEL MUNDO FIFA 2026* 🏆

📅 *Fechas:* 11 Junio - 19 Julio 2026

🌎 *Sedes:*
• 🇺🇸 Estados Unidos (11 ciudades)
• 🇲🇽 México (3 ciudades)
• 🇨🇦 Canadá (2 ciudades)

⚽ *Formato:*
• 48 selecciones (primera vez)
• 16 grupos de 3 equipos
• 104 partidos totales

🎯 *Predicciones del Bot:*

El bot tendrá análisis especial para el Mundial:
✅ Predicciones de fase de grupos
✅ Análisis de eliminación directa
✅ Seguimiento en tiempo real
✅ Estadísticas históricas de Mundiales
✅ Análisis de favoritos

📊 *Datos disponibles:*
• Rendimiento en eliminatorias
• Historial en Mundiales previos
• Forma actual de cada selección
• Head-to-head entre selecciones

💡 *Mientras tanto:*
Usa `/selecciones [país1] vs [país2]` para analizar amistosos y eliminatorias!

Ejemplos:
• `/selecciones Argentina vs Brasil`
• `/selecciones España vs Francia`
• `/selecciones Estados Unidos vs México`

🔥 ¡El bot estará listo con análisis completo para el Mundial 2026!
        """

        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    async def upcoming_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /proximos - Partidos de los próximos días"""
        # Determinar cuántos días mostrar
        days = 7  # Default: próxima semana

        if context.args:
            try:
                days = int(context.args[0])
                if days < 1 or days > 14:
                    days = 7
            except ValueError:
                days = 7

        await update.message.reply_text(
            f"🔍 Buscando partidos de los próximos {days} días..."
        )

        try:
            matches = self.analyzer.get_upcoming_matches(days_ahead=days)

            if not matches:
                await update.message.reply_text(
                    f"😔 No hay partidos programados para los próximos {days} días en las ligas principales."
                )
                return

            # Agrupar por fecha
            from collections import defaultdict
            matches_by_date = defaultdict(list)

            for match in matches:
                match_date = match.get('date', 'TBD')
                matches_by_date[match_date].append(match)

            response = f"⚽ *PARTIDOS PRÓXIMOS* ({days} días)\n\n"

            # Ordenar por fecha
            for date in sorted(matches_by_date.keys())[:10]:  # Máximo 10 fechas
                matches_on_date = matches_by_date[date]

                # Formatear fecha
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(date)
                    formatted_date = date_obj.strftime('%d/%m/%Y - %A')
                except:
                    formatted_date = date

                response += f"📅 *{formatted_date}*\n\n"

                for match in matches_on_date[:5]:  # Máximo 5 partidos por día
                    response += f"🏆 *{match.get('league', 'Liga')}*\n"
                    response += f"🏠 {match.get('home', match.get('home_team', 'TBD'))}"
                    response += f" vs {match.get('away', match.get('away_team', 'TBD'))} 🚗\n"
                    response += f"🕐 {match.get('time', 'TBD')}\n"

                    predictions = match.get('predictions', [])
                    if predictions:
                        best_pred = predictions[0]
                        conf_emoji = "🔥" if best_pred['confidence'] >= 80 else "✅"
                        response += f"{conf_emoji} *{best_pred['type']}* ({best_pred['confidence']}%)\n"

                    response += "\n"

                # Separador entre fechas
                if date != list(matches_by_date.keys())[-1]:
                    response += "━━━━━━━━━━━━━━━━━━━━\n\n"

            response += "\n💡 Usa `/partido [equipo1] vs [equipo2]` para análisis detallado"

            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error en /proximos: {e}")
            await update.message.reply_text(
                "❌ Error al obtener partidos próximos. Intenta de nuevo."
            )

    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /suscribir - Toggle notificaciones"""
        chat_id = update.effective_chat.id
        new_state = self.db.toggle_subscription(chat_id)

        if new_state:
            message = "✅ ¡Suscripción activada!\n\nRecibirás notificaciones diarias con las mejores predicciones."
        else:
            message = "❌ Suscripción desactivada.\n\nYa no recibirás notificaciones automáticas.\nPuedes reactivarla cuando quieras con /suscribir"

        await update.message.reply_text(message)

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar comandos desconocidos"""
        await update.message.reply_text(
            "❌ Comando no reconocido.\n"
            "Usa /help para ver los comandos disponibles."
        )

    def run(self):
        """Iniciar el bot"""
        logger.info("🤖 Iniciando Soccer Betting Bot...")

        # Crear aplicación
        self.app = Application.builder().token(self.token).build()

        # Registrar comandos
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("hoy", self.today_command))
        self.app.add_handler(CommandHandler("proximos", self.upcoming_command))
        self.app.add_handler(CommandHandler("analizar", self.analyze_command))
        self.app.add_handler(CommandHandler("partido", self.match_command))
        self.app.add_handler(CommandHandler("selecciones", self.international_command))
        self.app.add_handler(CommandHandler("mundial", self.worldcup_command))
        self.app.add_handler(CommandHandler("tendencias", self.trends_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        self.app.add_handler(CommandHandler("ligas", self.leagues_command))
        self.app.add_handler(CommandHandler("suscribir", self.subscribe_command))

        # Manejar mensajes desconocidos
        self.app.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))

        logger.info("✅ Bot configurado. Iniciando polling...")

        # Iniciar bot
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    # Cargar token desde .env
    from dotenv import load_dotenv
    load_dotenv()

    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    if not TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN no encontrado en .env")
        exit(1)

    # Iniciar bot
    bot = SoccerBettingBot(TOKEN)
    bot.run()
