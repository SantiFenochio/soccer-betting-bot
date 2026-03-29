# ⚽ Soccer Betting Analysis Bot

Bot de Telegram profesional que analiza datos de fútbol con IA y envía predicciones basadas en análisis multi-factorial.

## 🎯 Características

- **Análisis multi-factorial avanzado** con sistema de scoring de 100 puntos
- **Predicciones basadas en 5 factores**: Confianza base, Forma/Momentum, xG real, H2H, Value Bets
- **8 Skills de IA especializadas** que trabajan automáticamente
- **Expected Goals (xG)** con datos reales de Understat
- **Value Betting** con cálculo de Expected Value y Kelly Criterion
- **Bankroll Management** con tracking de ROI y estadísticas
- **Comando /fijini**: Top 3 mejores apuestas del día automáticas
- **Notificaciones por Telegram** con recomendaciones diarias
- **Comandos interactivos** para análisis profundo

## 🤖 Arquitectura de IA: Lead Agent + Skills

El bot usa una **arquitectura orquestada** con un lead agent coordinando múltiples skills:

### 🔥 Lead Agent
- **fijini-orchestrator** - Orquestador principal que coordina todo el análisis multi-factorial del comando `/fijini`

### 🔧 Worker Skills (8 especializadas)
- **football-data** ⚽ - 16 skills de datos de fútbol en tiempo real
- **sports-betting-analyzer** 🎲 - Identificación de value bets profesional
- **player-comparison-tool** 👥 - Comparación estadística de jugadores
- **injury-report-tracker** 🏥 - Monitor de lesiones y análisis de impacto
- **team-chemistry-evaluator** 🤝 - Evaluación de dinámica de equipos
- **game-strategy-simulator** 🎮 - Simulación de tácticas y estrategias
- **scouting-report-builder** 📊 - Reportes de scouting automáticos

### ⚡ Subagentes Paralelos
El fijini-orchestrator lanza **4 subagentes en paralelo** para máxima velocidad:
1. Data Fetcher - Obtiene todos los partidos del día
2. xG Analyzer - Analiza Expected Goals
3. Value Detector - Calcula Expected Value
4. Context Analyzer - Evalúa forma, H2H, lesiones

📖 **Ver documentación completa:** [SKILLS_INTEGRADAS.md](SKILLS_INTEGRADAS.md)

## 📊 Ligas Soportadas

- 🇪🇸 LaLiga (España)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)
- 🇩🇪 Bundesliga (Alemania)
- 🇮🇹 Serie A (Italia)
- 🇫🇷 Ligue 1 (Francia)
- 🇦🇷 Liga Profesional (Argentina)
- 🌍 Partidos Internacionales y Amistosos

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

### 🔥 Comandos Principales
- **`/fijini`** - 🏆 TOP 3 mejores apuestas del día (análisis completo del mercado)
- **`/partido [equipo1] vs [equipo2]`** - Análisis completo de partido específico
- **`/hoy`** - Todos los partidos y predicciones del día

### 📊 Análisis Avanzado
- **`/xg [equipo1] vs [equipo2]`** - Análisis Expected Goals con datos reales
- **`/h2h [equipo1] vs [equipo2]`** - Historial Head-to-Head últimos 5 partidos
- **`/momentum [equipo]`** - Análisis de forma y racha actual

### 💰 Bankroll Management
- **`/bankroll`** - Configurar/ver tu bankroll
- **`/balance`** - Ver estadísticas y ROI
- **`/apostar [detalles]`** - Registrar una apuesta
- **`/historial`** - Ver historial completo de apuestas
- **`/liquidar [id] [won/lost]`** - Liquidar apuesta

### ℹ️ Información
- **`/start`** - Iniciar el bot y obtener tu chat ID
- **`/help`** - Ayuda y comandos disponibles
- **`/ligas`** - Ver todas las ligas disponibles

📖 **Ver documentación completa:** [COMANDO_FIJINI.md](COMANDO_FIJINI.md)

## 📈 Tipos de Predicciones y Análisis

### Predicciones de Apuestas
- **Over/Under goles** - Basado en xG real y H2H
- **Ambos equipos marcan (BTTS)** - Con análisis de forma ofensiva
- **Resultado exacto (1X2)** - Victoria Local/Empate/Victoria Visitante
- **Value Bets** - Apuestas con Expected Value positivo
- **Córners y tarjetas** - Análisis estadístico de promedios

### Sistema de Rating
- ⭐⭐⭐⭐⭐ (90-100 pts) - Lock máximo, apuesta con confianza
- ⭐⭐⭐⭐ (80-89 pts) - Muy confiable, apuesta fuerte
- ⭐⭐⭐ (75-79 pts) - Confiable, apuesta moderada

### Factores de Análisis (100 puntos)
1. **Confianza Base** (30 pts) - Predicción del modelo principal
2. **Forma/Momentum** (20 pts) - Últimos 5 partidos, racha actual
3. **Expected Goals (xG)** (20 pts) - Datos reales de Understat
4. **Head-to-Head** (15 pts) - Últimos 5 enfrentamientos
5. **Expected Value** (15 pts) - Cálculo de EV y value bets

📖 **Ver metodología completa:** [COMANDO_FIJINI.md](COMANDO_FIJINI.md)

## 📚 Documentación

- **[QUICKSTART.md](QUICKSTART.md)** - Inicio rápido en 5 minutos
- **[COMANDO_FIJINI.md](COMANDO_FIJINI.md)** - Guía completa del comando /fijini
- **[SKILLS_INTEGRADAS.md](SKILLS_INTEGRADAS.md)** - Skills de IA y cómo usarlas
- **[MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md)** - Todas las mejoras del bot
- **[MEJORAS_PROPUESTAS.md](MEJORAS_PROPUESTAS.md)** - 50+ mejoras futuras investigadas

## 🔥 Últimas Mejoras (Marzo 2026)

### ⚡ Mejora #5: Skills de IA Integradas
- ✅ 8 skills especializadas instaladas
- ✅ football-data: 16 skills de datos en tiempo real
- ✅ sports-betting-analyzer: Análisis profesional de apuestas
- ✅ injury-report-tracker: Monitor de lesiones automático
- ✅ Mejoras automáticas en todos los comandos

### 🏆 Mejora #4: Comando /fijini
- ✅ Analiza TODO el mercado del día automáticamente
- ✅ Sistema multi-factorial de 100 puntos
- ✅ Top 3 mejores apuestas con rating de estrellas
- ✅ Considera: confianza, forma, xG, H2H, value bets
- ✅ Bonus de consistencia cuando 3+ factores son altos

### 💰 Mejora #3: Bankroll Management Completo
- ✅ Sistema de tracking con base de datos SQLite
- ✅ Registro y liquidación de apuestas
- ✅ Estadísticas: ROI, win rate, profit/loss
- ✅ Historial completo con filtros
- ✅ Kelly Criterion para sizing óptimo

### 📊 Mejora #2: Análisis Avanzado
- ✅ Expected Goals (xG) con datos reales de Understat
- ✅ Value Betting con cálculo de Expected Value
- ✅ Head-to-Head últimos 5 enfrentamientos
- ✅ Momentum y análisis de racha
- ✅ Detección de arbitraje (surebets)

### 🌍 Mejora #1: Partidos Internacionales
- ✅ Soporte para amistosos y competiciones internacionales
- ✅ Copa América, Mundiales, Nations League
- ✅ Búsqueda por fecha completa (no solo ligas específicas)

## ⚠️ Disclaimer

Este bot proporciona análisis estadístico con fines educativos.
**Ninguna predicción es 100% segura.**
Las apuestas pueden causar adicción. Juega responsablemente.

## 📝 Licencia

MIT
