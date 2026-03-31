# ⚽ Soccer Betting Bot

Bot de Telegram para análisis y predicciones de partidos de fútbol usando Machine Learning y datos estadísticos reales.

## 🎯 ¿Qué hace?

Analiza partidos de fútbol de las principales ligas europeas y sudamericanas usando:

- **Machine Learning (XGBoost)** - Modelos entrenados con datos históricos (~67% precisión)
- **Expected Goals (xG)** - Datos reales scrapeados de Understat y FBref
- **Análisis de forma** - Últimos 5 partidos y momentum del equipo
- **Head-to-Head** - Histórico de enfrentamientos directos
- **Scoring multi-factorial** - Sistema de 100 puntos que combina múltiples factores

## 📊 Ligas Soportadas

- 🇪🇸 LaLiga (España)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)
- 🇩🇪 Bundesliga (Alemania)
- 🇮🇹 Serie A (Italia)
- 🇫🇷 Ligue 1 (Francia)
- 🇦🇷 Liga Profesional (Argentina)

## 🚀 Instalación

### 1. Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `python-telegram-bot` - Bot de Telegram
- `soccerdata==1.5.1` - Scraping de datos de fútbol (FBref + Understat)
- `xgboost` + `scikit-learn` - Machine Learning
- `pandas`, `numpy` - Análisis de datos
- `schedule` - Notificaciones automáticas

### 2. Configuración

Crea un archivo `.env` con tu token de Telegram:

```
TELEGRAM_BOT_TOKEN=tu_token_aquí
TELEGRAM_CHAT_ID=tu_chat_id (opcional)
```

### 3. Ejecutar

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
# Opción 3 (Bot + Scheduler)
```

## 💬 Comandos

### 🔥 Principales
- `/fijini` - Top 3 mejores apuestas (próximas 48hs)
- `/hoy` - Todos los partidos de hoy con predicciones

### 📊 Análisis Específico
- `/partido [equipo1] vs [equipo2]` - Predicción completa
- `/xg [equipo1] vs [equipo2]` - Análisis Expected Goals
- `/h2h [equipo1] vs [equipo2]` - Historial head-to-head
- `/momentum [equipo]` - Forma y racha actual

### ℹ️ Información
- `/stats` - Precisión del bot
- `/ligas` - Ligas disponibles
- `/help` - Ayuda completa

## 🤖 Machine Learning

Los modelos ya están entrenados y listos en `models/`:
- `result_model.pkl` - Predicción de resultado (1X2)
- `total_goals_model.pkl` - Predicción de goles totales
- `btts_model.pkl` - Ambos equipos anotan

**Reentrenamiento automático:** Cada domingo a las 3:00 AM

**Reentrenar manualmente:**
```bash
python train_ml.py
```

## ⚠️ Disclaimer

Este bot proporciona análisis estadístico con fines educativos.
**No hay predicciones 100% seguras.** Las apuestas pueden causar adicción.
Juega responsablemente.

## 📝 Licencia

MIT
