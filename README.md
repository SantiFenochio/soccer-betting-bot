# ⚽ Soccer Betting Analysis Bot

Bot de Telegram profesional ultra-potente con análisis multi-factorial usando 11 skills especializadas de IA.

## 🎯 Características

- **🔥 /fijini** - TOP 3 LOCKS próximas 48hs (hoy + mañana)
- **📅 /hoy** - Análisis completo de todos los partidos del día
- **Análisis ultra-potente** con 11 skills integradas de IA
- **Sistema de scoring de 100 puntos** con 5 factores principales
- **Expected Goals (xG)** con datos REALES de Understat/FBref
- **Odds de 10+ bookmakers** con cálculo de Expected Value
- **Análisis multi-dimensional**: xG + Form + H2H + Value + Injuries + Chemistry + Strategy
- **Notificaciones por Telegram** con recomendaciones diarias
- **Comandos interactivos** para análisis profundo

## 🤖 Arquitectura de IA: 11 Skills Integradas

El bot usa una **arquitectura orquestada ultra-potente** con 11 skills especializadas:

### 🔥 Lead Agent (1)
- **fijini-orchestrator** - Orquestador principal que coordina análisis multi-factorial para `/fijini`

### ⚽ Data Providers (3)
- **understat-xg-integrator** - Datos xG REALES de Understat/FBref (no estimados)
- **full-odds-multi-bookmaker** - Odds reales de 10+ bookmakers (Bet365, Pinnacle, etc.)
- **football-data** ⚽ - 16 sub-skills de datos de fútbol en tiempo real

### 🔧 Analyzer Skills (7 especializadas)
- **sports-betting-analyzer** 🎲 - Identificación de value bets profesional
- **player-comparison-tool** 👥 - Comparación estadística de jugadores clave
- **injury-report-tracker** 🏥 - Monitor de lesiones y análisis de impacto
- **team-chemistry-evaluator** 🤝 - Evaluación de cohesión y dinámica
- **game-strategy-simulator** 🎮 - Simulación de tácticas y estrategias
- **scouting-report-builder** 📊 - Reportes de scouting completos

### ⚡ Análisis Paralelo
El fijini-orchestrator lanza **4 subagentes en paralelo** para máxima velocidad:
1. **Data Fetcher** - Obtiene todos los partidos de próximas 48hs
2. **xG Analyzer** - Analiza Expected Goals reales
3. **Value Detector** - Calcula Expected Value de odds
4. **Context Analyzer** - Evalúa forma, H2H, lesiones, química, táctica

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

2. **✅ Modelos ML ya entrenados**
   - Los modelos de Machine Learning YA ESTÁN entrenados y listos
   - Ubicación: `models/` (4 archivos .pkl)
   - No necesitas hacer nada más
   - El bot se reentrenará automáticamente cada domingo

   **Opcional:** Reentrenar manualmente
   ```bash
   python train_ml.py
   ```
   Ver [ML_README.md](ML_README.md) para más detalles.

3. **Ya tienes el token configurado** en `.env` ✅
   - Si necesitas cambiarlo, edita el archivo `.env`

4. **Ejecutar el bot**

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

### 🔥 Comandos Principales (Ultra-Potentes)
- **`/fijini`** - 🏆 TOP 3 LOCKS próximas 48hs (hoy + mañana)
  - Análisis ultra-potente con 11 skills integradas
  - Sistema de scoring de 100 puntos
  - Las 3 mejores apuestas del mercado
- **`/hoy`** - 📅 Análisis completo de todos los partidos del día
  - Predicciones con scoring profesional
  - Recomendaciones claras con confianza %

### 📊 Análisis Específico
- **`/partido [equipo1] vs [equipo2]`** - Análisis completo de un partido
- **`/xg [equipo1] vs [equipo2]`** - Análisis Expected Goals con datos reales
- **`/h2h [equipo1] vs [equipo2]`** - Historial Head-to-Head últimos 5 partidos
- **`/momentum [equipo]`** - Análisis de forma y racha actual

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
1. **🤖 Base Confidence (30 pts)** - Modelo ML con XGBoost entrenado con datos históricos
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

### 🤖 Mejora #9: Machine Learning con XGBoost (30 Marzo 2026)
- ✅ **Modelo ML entrenado con datos históricos** de 4-5 temporadas
- ✅ **15+ features** extraídas por partido (xG, forma, momentum, H2H, etc.)
- ✅ **3 modelos especializados**: Resultado (1X2), Goles totales, BTTS
- ✅ **Base Confidence (30 pts)** del scoring ahora usa predicción ML
- ✅ **Reentrenamiento automático semanal** con datos actualizados
- ✅ **Accuracy real del modelo** mostrado en predicciones
- ✅ **Fallback graceful** si ML no disponible
- 📊 **Precisión esperada**: 65-70% en resultados, mejor en goles/BTTS

### ✅ Mejora #8: Verificación Automática de Resultados (30 Marzo 2026)
- ✅ **Job diario a las 23:00** verifica predicciones del día anterior
- ✅ **Consulta API** para obtener resultados reales de partidos
- ✅ **Actualiza base de datos** automáticamente (correct/incorrect + score)
- ✅ **Accuracy real calculado** solo sobre predicciones verificadas
- ✅ **Tracking de performance** por tipo de apuesta
- ✅ **Mejora continua** del sistema basado en resultados reales

## 🔥 Mejoras Anteriores

### 💰 Mejora #7: full-odds-multi-bookmaker
- ✅ Odds reales de 10+ bookmakers
- ✅ Compara Bet365, Pinnacle, William Hill, Betfair, 1xBet, etc.
- ✅ Encuentra la mejor cuota disponible
- ✅ Calcula Expected Value (EV) real
- ✅ Scoring 0-15 puntos (Factor 5)
- ✅ Integración con fijini-orchestrator
- ✅ Cobertura: 12+ ligas principales

### 🎯 Mejora #6: understat-xg-integrator
- ✅ Datos xG REALES de Understat.com (no estimados)
- ✅ Fallback automático a FBref.com
- ✅ Cache de 6 horas + rate limiting
- ✅ Scoring de 0-20 puntos para factor xG
- ✅ Integración automática con fijini-orchestrator
- ✅ Cobertura: Top 5 ligas europeas

### ⚡ Mejora #5: Skills de IA Integradas
- ✅ 10 skills especializadas instaladas (1 lead + 2 data + 7 analyzers)
- ✅ fijini-orchestrator: Lead agent orquestador
- ✅ football-data: 16 skills de datos en tiempo real
- ✅ sports-betting-analyzer: Análisis profesional de apuestas
- ✅ injury-report-tracker: Monitor de lesiones automático
- ✅ Mejoras automáticas en todos los comandos

### 🏆 Mejora #4: Comando /fijini Ultra-Potente
- ✅ Analiza próximas 48 horas (hoy + mañana) automáticamente
- ✅ Sistema multi-factorial de 100 puntos con 11 skills
- ✅ Top 3 mejores apuestas con rating de estrellas
- ✅ Considera: confianza, forma, xG real, H2H, value bets, injuries, chemistry, strategy
- ✅ Bonus de consistencia cuando 3+ factores son altos
- ✅ Prioriza partidos de hoy vs mañana inteligentemente

### 📊 Mejora #3: Análisis Avanzado Multi-Dimensional
- ✅ Expected Goals (xG) con datos REALES de Understat/FBref
- ✅ Value Betting con cálculo de Expected Value real
- ✅ Odds de 10+ bookmakers comparadas en tiempo real
- ✅ Head-to-Head últimos 5 enfrentamientos
- ✅ Momentum y análisis de racha profesional
- ✅ Análisis de lesiones, química de equipo, táctica
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
