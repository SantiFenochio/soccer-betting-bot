"""
Simple Soccer Betting Bot
Bot de Telegram simplificado para detección de value bets
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

from value_bets import ValueBetFinder
from data_fetcher import DataFetcher

# Fix para emojis en Windows
if sys.platform == 'win32':
    import codecs
    # Solo aplicar si aún no se aplicó
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Mapeo de códigos de liga a IDs
LEAGUES = {
    'PL': {'id': 2021, 'name': 'Premier League'},
    'PD': {'id': 2014, 'name': 'La Liga'},
    'BL1': {'id': 2002, 'name': 'Bundesliga'},
    'SA': {'id': 2019, 'name': 'Serie A'},
    'FL1': {'id': 2015, 'name': 'Ligue 1'},
}


class SoccerBettingBot:
    """Bot de Telegram simple para value bets"""

    def __init__(self, token: str):
        """Inicializar bot"""
        self.token = token
        self.value_finder = ValueBetFinder()
        self.data_fetcher = self.value_finder.data_fetcher

        logger.info("Bot inicializado")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user

        message = f"""
🎯 *Soccer Betting Bot - Value Finder*

¡Hola {user.first_name}! 👋

Detecto value bets automáticamente usando:
• 📊 football-data.org (stats de equipos)
• 💰 The Odds API (odds reales)
• 🧮 Modelo Poisson (cálculo de EV)

*COMANDOS DISPONIBLES:*

🔍 */analizar [liga]* - Buscar value bets
   Ejemplo: `/analizar PL`

📅 */partidos [liga]* - Próximos partidos
   Ejemplo: `/partidos PD`

⚙️ */estado* - Estado de APIs

💡 */ayuda* - Ver esta ayuda

*LIGAS SOPORTADAS:*
• PL - Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿
• PD - La Liga 🇪🇸
• BL1 - Bundesliga 🇩🇪
• SA - Serie A 🇮🇹
• FL1 - Ligue 1 🇫🇷

⚠️ _Apuesta responsablemente_
        """

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def ayuda_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /ayuda"""
        message = """
📖 *GUÍA DE COMANDOS*

🔍 *ANALIZAR VALUE BETS*
`/analizar [liga]`

Busca partidos con Expected Value positivo (>5%)

Ejemplos:
• `/analizar PL` - Premier League
• `/analizar PD` - La Liga
• `/analizar BL1` - Bundesliga

---

📅 *VER PRÓXIMOS PARTIDOS*
`/partidos [liga]`

Lista los próximos 5 partidos programados

Ejemplos:
• `/partidos SA` - Serie A
• `/partidos FL1` - Ligue 1

---

⚙️ *ESTADO DEL SISTEMA*
`/estado`

Verifica:
• Conexión a football-data.org
• Conexión a The Odds API
• Requests restantes (The Odds API)

---

*LIGAS DISPONIBLES:*
PL, PD, BL1, SA, FL1

⚠️ _El análisis consume requests de The Odds API (límite: 500/mes en free tier)_
        """

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    async def analizar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /analizar [liga]"""
        # Verificar argumentos
        if not context.args:
            await update.message.reply_text(
                "⚠️ *Uso incorrecto*\n\n"
                "Usa: `/analizar [liga]`\n\n"
                "Ejemplos:\n"
                "• `/analizar PL` - Premier League\n"
                "• `/analizar PD` - La Liga\n"
                "• `/analizar BL1` - Bundesliga\n\n"
                "Ligas: PL, PD, BL1, SA, FL1",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        league_code = context.args[0].upper()

        # Verificar liga válida
        if league_code not in LEAGUES:
            await update.message.reply_text(
                f"❌ Liga '{league_code}' no soportada\n\n"
                "Ligas disponibles:\n"
                "• PL - Premier League\n"
                "• PD - La Liga\n"
                "• BL1 - Bundesliga\n"
                "• SA - Serie A\n"
                "• FL1 - Ligue 1",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        league = LEAGUES[league_code]
        league_name = league['name']
        competition_id = league['id']

        # Mensaje de "analizando"
        status_msg = await update.message.reply_text(
            f"⏳ *Analizando {league_name}...*\n\n"
            f"• Obteniendo próximos partidos\n"
            f"• Buscando odds reales\n"
            f"• Calculando Expected Value\n\n"
            f"_Esto puede tardar 10-30 segundos_",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            # Buscar value bets
            logger.info(f"Usuario {update.effective_user.id} solicitó análisis de {league_name}")
            value_bets = self.value_finder.find_value_in_competition(competition_id)

            # Eliminar mensaje de "analizando"
            await status_msg.delete()

            if not value_bets:
                await update.message.reply_text(
                    f"😕 *No se encontraron value bets en {league_name}*\n\n"
                    f"Posibles razones:\n"
                    f"• No hay partidos próximos\n"
                    f"• Las odds actuales no ofrecen value\n"
                    f"• Requests de The Odds API agotados\n\n"
                    f"Intenta más tarde o con otra liga.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Enviar value bets encontrados
            response = f"🔥 *VALUE BETS - {league_name}*\n\n"
            response += f"Encontrados: *{len(value_bets)} partidos*\n"
            response += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"

            for i, bet in enumerate(value_bets[:5], 1):  # Top 5
                response += f"*{i}. {bet['home_team']} vs {bet['away_team']}*\n"

                # Fecha
                try:
                    date_str = bet.get('match_date', '')
                    if date_str:
                        date = datetime.fromisoformat(date_str)
                        response += f"📅 {date.strftime('%d/%m/%Y %H:%M')}\n"
                except:
                    pass

                response += f"\n"
                response += f"🎯 *{bet['recommendation']}*\n"
                response += f"💰 Apuesta: {bet['best_bet']} @ {bet['best_odds']}\n"
                response += f"📈 Expected Value: *+{bet['best_ev']*100:.1f}%*\n"
                response += f"⭐ Confianza: {bet['confidence']}%\n"

                # Stats
                home_stats = bet['stats']['home']
                away_stats = bet['stats']['away']
                response += f"\n📊 Stats:\n"
                response += f"   • {bet['home_team']}: ATK {home_stats['attack']} | DEF {home_stats['defense']} | FORM {home_stats['form']}\n"
                response += f"   • {bet['away_team']}: ATK {away_stats['attack']} | DEF {away_stats['defense']} | FORM {away_stats['form']}\n"

                response += f"\n{'─'*30}\n\n"

            response += f"⚠️ _Apuesta responsablemente. El EV positivo no garantiza ganancia._"

            # Enviar (puede ser largo, dividir si es necesario)
            if len(response) > 4000:
                # Enviar en chunks
                for i in range(0, len(response), 4000):
                    await update.message.reply_text(
                        response[i:i+4000],
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

            # Mostrar requests restantes
            if self.data_fetcher.odds_requests_remaining:
                await update.message.reply_text(
                    f"📊 Requests restantes (The Odds API): {self.data_fetcher.odds_requests_remaining}",
                    parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            logger.error(f"Error en /analizar: {e}", exc_info=True)
            await status_msg.delete()
            await update.message.reply_text(
                f"❌ *Error al analizar*\n\n"
                f"Error: {str(e)}\n\n"
                f"Verifica el estado de las APIs con `/estado`",
                parse_mode=ParseMode.MARKDOWN
            )

    async def partidos_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /partidos [liga]"""
        # Verificar argumentos
        if not context.args:
            await update.message.reply_text(
                "⚠️ *Uso incorrecto*\n\n"
                "Usa: `/partidos [liga]`\n\n"
                "Ejemplos:\n"
                "• `/partidos PL`\n"
                "• `/partidos PD`\n\n"
                "Ligas: PL, PD, BL1, SA, FL1",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        league_code = context.args[0].upper()

        if league_code not in LEAGUES:
            await update.message.reply_text(
                f"❌ Liga '{league_code}' no soportada\n\n"
                "Ligas: PL, PD, BL1, SA, FL1"
            )
            return

        league = LEAGUES[league_code]
        league_name = league['name']
        competition_id = league['id']

        try:
            # Obtener próximos partidos
            status_msg = await update.message.reply_text(
                f"⏳ Obteniendo partidos de {league_name}..."
            )

            upcoming = self.data_fetcher.get_upcoming_matches(competition_id, days_ahead=14)

            await status_msg.delete()

            if not upcoming:
                await update.message.reply_text(
                    f"😕 No hay partidos próximos en {league_name}\n\n"
                    f"Posiblemente sea fuera de temporada.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            # Formatear respuesta
            response = f"📅 *PRÓXIMOS PARTIDOS - {league_name}*\n\n"

            for i, match in enumerate(upcoming[:5], 1):
                response += f"*{i}. {match['home_team']} vs {match['away_team']}*\n"

                # Fecha
                try:
                    date = datetime.fromisoformat(match['date'])
                    response += f"   🕐 {date.strftime('%d/%m/%Y %H:%M')}\n"
                except:
                    response += f"   🕐 {match.get('date', 'TBD')}\n"

                response += f"   🏆 Jornada {match.get('matchday', 'N/A')}\n"
                response += "\n"

            response += f"Total programados: {len(upcoming)} partidos"

            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error en /partidos: {e}", exc_info=True)
            await update.message.reply_text(
                f"❌ Error obteniendo partidos\n\n{str(e)}"
            )

    async def estado_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /estado"""
        status_msg = await update.message.reply_text("⏳ Verificando APIs...")

        response = "⚙️ *ESTADO DEL SISTEMA*\n\n"

        # Test football-data.org
        try:
            comps = self.data_fetcher.get_competitions()
            if comps:
                response += "✅ *football-data.org*: Funcionando\n"
                response += f"   • {len(comps)} competiciones disponibles\n"
            else:
                response += "⚠️ *football-data.org*: Sin respuesta\n"
        except Exception as e:
            response += f"❌ *football-data.org*: Error\n"
            response += f"   • {str(e)[:50]}\n"

        response += "\n"

        # Test The Odds API
        if self.data_fetcher.odds_api_key:
            response += "✅ *The Odds API*: Configurada\n"

            if self.data_fetcher.odds_requests_remaining is not None:
                remaining = self.data_fetcher.odds_requests_remaining
                response += f"   • Requests restantes: *{remaining}*\n"

                if remaining < 50:
                    response += f"   • ⚠️ Quedan menos de 50 requests\n"
                elif remaining < 100:
                    response += f"   • ⚡ Usar con moderación\n"
                else:
                    response += f"   • ✓ Suficientes requests\n"
            else:
                response += "   • No se han usado requests aún\n"
                response += "   • Límite: 500 requests/mes (free tier)\n"
        else:
            response += "❌ *The Odds API*: No configurada\n"
            response += "   • ODDS_API_KEY no encontrada en .env\n"

        response += "\n"
        response += f"🕐 Última verificación: {datetime.now().strftime('%H:%M:%S')}"

        await status_msg.delete()
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar errores"""
        logger.error(f"Error: {context.error}", exc_info=context.error)

        try:
            if update and update.message:
                await update.message.reply_text(
                    "❌ Ocurrió un error inesperado.\n\n"
                    "Intenta nuevamente o usa /estado para verificar las APIs."
                )
        except:
            pass

    def run(self):
        """Ejecutar bot"""
        logger.info("Iniciando Soccer Betting Bot...")

        # Crear application
        app = Application.builder().token(self.token).build()

        # Registrar handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("ayuda", self.ayuda_command))
        app.add_handler(CommandHandler("help", self.ayuda_command))
        app.add_handler(CommandHandler("analizar", self.analizar_command))
        app.add_handler(CommandHandler("partidos", self.partidos_command))
        app.add_handler(CommandHandler("estado", self.estado_command))

        # Error handler
        app.add_error_handler(self.error_handler)

        # Iniciar
        logger.info("Bot listo - esperando comandos...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN no encontrado en .env")
        return

    try:
        bot = SoccerBettingBot(token)
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot detenido por usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)


if __name__ == '__main__':
    main()
