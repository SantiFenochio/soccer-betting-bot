# Soccer Betting Bot - Guía de Uso

## 🎯 Bot Simplificado

Bot de Telegram reescrito desde cero: **442 líneas** (antes: 893 líneas)

## 🚀 Iniciar el Bot

```bash
python bot.py
```

O usar el script de inicio:
```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

## 💬 Comandos Disponibles

### `/start`
Mensaje de bienvenida con lista de comandos disponibles.

### `/analizar [liga]`
Busca value bets en la liga especificada usando:
- Datos de partidos de football-data.org
- Odds reales de The Odds API
- Modelo Poisson para calcular Expected Value

**Ejemplos:**
```
/analizar PL     → Premier League
/analizar PD     → La Liga
/analizar BL1    → Bundesliga
/analizar SA     → Serie A
/analizar FL1    → Ligue 1
```

**Output:**
- Top 5 value bets encontrados
- Expected Value de cada apuesta
- Confianza del modelo (0-100%)
- Stats de ambos equipos
- Bookmaker y odds

### `/partidos [liga]`
Lista los próximos 5 partidos programados de la liga.

**Ejemplos:**
```
/partidos PL     → Próximos partidos Premier League
/partidos PD     → Próximos partidos La Liga
```

**Output:**
- Equipos (Local vs Visitante)
- Fecha y hora del partido
- Número de jornada

### `/estado`
Verifica el estado de las APIs y muestra información del sistema.

**Output:**
- ✅/❌ Estado de football-data.org
- ✅/❌ Estado de The Odds API
- Requests restantes (The Odds API)
- Última verificación

### `/ayuda` o `/help`
Muestra la guía completa de comandos.

## 🔑 Códigos de Ligas

| Código | Liga | País |
|--------|------|------|
| PL | Premier League | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra |
| PD | La Liga | 🇪🇸 España |
| BL1 | Bundesliga | 🇩🇪 Alemania |
| SA | Serie A | 🇮🇹 Italia |
| FL1 | Ligue 1 | 🇫🇷 Francia |

## ⚙️ Variables de Entorno

Necesitas estas variables en `.env`:

```bash
# Bot de Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui

# APIs de datos
FOOTBALL_DATA_KEY=tu_key_aqui
ODDS_API_KEY=tu_key_aqui
```

## 📊 Límites de Rate

### The Odds API (Free Tier)
- **500 requests/mes**
- ~16 requests/día si se distribuye uniformemente
- Cada `/analizar` consume 1-6 requests (dependiendo de cuántos partidos encuentra)
- El bot se pausa automáticamente si quedan < 50 requests

### football-data.org (Free Tier)
- **10 requests/minuto**
- Respuestas cacheadas por 1 hora
- Rate limit 429 → retry automático después de 60s

## ⏱️ Tiempos de Respuesta

| Comando | Tiempo Estimado |
|---------|----------------|
| `/start` | Instantáneo |
| `/ayuda` | Instantáneo |
| `/estado` | 2-5 segundos |
| `/partidos [liga]` | 2-5 segundos |
| `/analizar [liga]` | 10-30 segundos |

**Nota:** `/analizar` muestra mensaje de "⏳ Analizando..." mientras trabaja.

## ❌ Manejo de Errores

El bot maneja errores comunes y muestra mensajes claros:

### Sin partidos próximos
```
😕 No se encontraron value bets en Premier League

Posibles razones:
• No hay partidos próximos
• Las odds actuales no ofrecen value
• Requests de The Odds API agotados

Intenta más tarde o con otra liga.
```

### API no disponible
```
❌ Error al analizar

Error: Connection timeout

Verifica el estado de las APIs con /estado
```

### Uso incorrecto
```
⚠️ Uso incorrecto

Usa: /analizar [liga]

Ejemplos:
• /analizar PL - Premier League
• /analizar PD - La Liga
```

## 🧪 Testing

Verifica que el bot funcione correctamente:

```python
# Test de importación
python -c "from bot import SoccerBettingBot; print('✓ Bot importado correctamente')"

# Test de sintaxis
python -m py_compile bot.py
```

## 📝 Características del Nuevo Bot

### ✅ Lo que SÍ tiene:
- Comandos esenciales funcionales
- Integración directa con ValueBetFinder
- Manejo robusto de errores
- Mensajes claros al usuario
- Logging completo
- Soporte para python-telegram-bot v20+

### ❌ Lo que NO tiene (simplificado):
- Sistema de suscripciones
- Base de datos de usuarios
- Roles de admin
- Comandos de configuración
- Sistema de notificaciones automáticas
- Comandos obsoletos (/xg, /h2h, /momentum, etc.)

## 🔧 Troubleshooting

### Bot no responde
1. Verificar que `TELEGRAM_BOT_TOKEN` está en `.env`
2. Verificar que el bot tiene permisos en Telegram
3. Ver logs para errores

### "No se encontraron value bets"
1. Verificar que hay partidos próximos en la liga
2. Usar `/estado` para verificar APIs
3. Verificar requests restantes de The Odds API

### Error de APIs
1. Usar `/estado` para diagnosticar
2. Verificar API keys en `.env`
3. Verificar conectividad a internet
4. Ver logs para detalles del error

## 📖 Ejemplo de Uso Completo

```
Usuario: /start
Bot: [Mensaje de bienvenida con comandos]

Usuario: /estado
Bot: 
⚙️ ESTADO DEL SISTEMA

✅ football-data.org: Funcionando
   • 39 competiciones disponibles

✅ The Odds API: Configurada
   • Requests restantes: 485
   • ✓ Suficientes requests

🕐 Última verificación: 17:30:45

Usuario: /analizar PL
Bot: ⏳ Analizando Premier League...
     • Obteniendo próximos partidos
     • Buscando odds reales
     • Calculando Expected Value
     
     [10-30 segundos después]
     
     🔥 VALUE BETS - Premier League
     
     Encontrados: 2 partidos
     ━━━━━━━━━━━━━━━━━━━━━━
     
     1. Arsenal vs Liverpool
     📅 05/04/2026 15:00
     
     🎯 🔥🔥 GOOD VALUE BET - HOME
     💰 Apuesta: HOME @ 2.10
     📈 Expected Value: +13.1%
     ⭐ Confianza: 85%
     
     📊 Stats:
        • Arsenal: ATK 63 | DEF 90 | FORM 83
        • Liverpool: ATK 56 | DEF 54 | FORM 60
     
     [...]
     
     ⚠️ Apuesta responsablemente. El EV positivo no garantiza ganancia.
     
     📊 Requests restantes (The Odds API): 480
```

## 🎓 Conceptos Clave

### Expected Value (EV)
```
EV = (Probabilidad_Modelo × Odds_Real) - 1

EV > 0.15 → 🔥🔥🔥 EXCELENTE
EV > 0.10 → 🔥🔥 MUY BUENO
EV > 0.05 → 🔥 BUENO
EV > 0    → ⚡ LEVE
EV < 0    → ❌ SIN VALOR
```

Solo se reportan value bets con **EV > 5%**.

### Confianza
Basada en el Expected Value:
- **95%**: EV > 15%
- **85%**: EV > 10%
- **75%**: EV > 5%
- **60%**: EV > 0%

### Stats de Equipos
- **ATK** (Attack): 0-100, basado en goles anotados
- **DEF** (Defense): 0-100, basado en goles recibidos (invertido)
- **FORM** (Forma): 0-100, basado en puntos de últimos 10 partidos

Calculados con datos reales de football-data.org.
