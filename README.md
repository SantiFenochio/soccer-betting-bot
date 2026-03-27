# ⚽ Soccer Betting Analysis Bot

Bot de Telegram que analiza datos de fútbol y envía predicciones basadas en estadísticas históricas.

## 🎯 Características

- **Análisis automático** de partidos de las principales ligas
- **Predicciones basadas en datos** de múltiples fuentes (FBref, Understat, etc.)
- **Notificaciones por Telegram** con recomendaciones diarias
- **Comandos interactivos** para consultas específicas
- **Tracking de resultados** para medir precisión

## 📊 Ligas Soportadas

- 🇪🇸 LaLiga (España)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)
- 🇩🇪 Bundesliga (Alemania)
- 🇮🇹 Serie A (Italia)
- 🇫🇷 Ligue 1 (Francia)
- 🇦🇷 Liga Profesional (Argentina)

## 🚀 Instalación

### ⚡ Inicio Rápido

**Todo en 5 minutos:** Ver [QUICKSTART.md](QUICKSTART.md)

### 📦 Instalación Paso a Paso

1. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

2. **Ya tienes el token configurado** en `.env` ✅
   - Si necesitas cambiarlo, edita el archivo `.env`

3. **Ejecutar el bot**

   **Windows:**
   ```bash
   run.bat
   ```

   **Linux/Mac:**
   ```bash
   ./run.sh
   ```

   **Manual:**
   ```bash
   python main.py
   # Selecciona opción 3 (recomendado)
   ```

4. **Configurar tu Chat ID**
   - Envía `/start` a tu bot en Telegram
   - Copia el Chat ID que te muestra
   - Agrégalo en `.env`: `TELEGRAM_CHAT_ID=tu_id`

Ver guía completa: [INSTALL.md](INSTALL.md)

## 💬 Comandos del Bot

- `/start` - Iniciar el bot y obtener tu chat ID
- `/analizar [equipo]` - Análisis completo de un equipo
- `/partido [equipo1] vs [equipo2]` - Predicción de partido específico
- `/hoy` - Partidos y predicciones del día
- `/tendencias` - Patrones estadísticos más confiables
- `/stats [jugador]` - Estadísticas de un jugador
- `/ligas` - Ver todas las ligas disponibles
- `/help` - Ayuda y comandos disponibles

## 📈 Tipos de Predicciones

- **Over/Under goles** - Total de goles en el partido
- **Ambos equipos marcan (BTTS)** - Both Teams To Score
- **Resultado exacto** - 1X2
- **Córners** - Total de córners
- **Tarjetas** - Total de tarjetas amarillas/rojas

## ⚠️ Disclaimer

Este bot proporciona análisis estadístico con fines educativos.
**Ninguna predicción es 100% segura.**
Las apuestas pueden causar adicción. Juega responsablemente.

## 📝 Licencia

MIT
