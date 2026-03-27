# 📱 Lista Completa de Comandos del Bot

## ✅ Estado Actual

- ✅ Token de Telegram configurado
- ✅ Chat ID configurado (882530352)
- ✅ **API-Football configurada** (partidos futuros)
- ✅ **The Odds API configurada** (cuotas de apuestas)
- ✅ **Football-Data.org configurada** (datos adicionales)
- ✅ Todas las dependencias instaladas
- ✅ Bot listo para usar con análisis profesional

---

## 🎮 Comandos de Inicio

### `/start`
**Descripción:** Iniciar el bot y obtener bienvenida
**Uso:** `/start`
**Respuesta:** Mensaje de bienvenida + tu Chat ID + lista de comandos

---

### `/help`
**Descripción:** Ver ayuda y lista de comandos
**Uso:** `/help`
**Respuesta:** Guía de todos los comandos con ejemplos

---

## ⚽ Comandos de Partidos (Clubes)

### `/hoy`
**Descripción:** Ver partidos de hoy con predicciones
**Uso:** `/hoy`
**Fuentes:** FBref, API-Football (si disponible)
**Respuesta:**
```
⚽ PARTIDOS DE HOY

🏆 Premier League
🏠 Manchester City vs Liverpool 🚗
🕐 20:00
🔥 Over 2.5 goles (85%)
```

---

### `/proximos` o `/proximos [días]` 🆕
**Descripción:** Ver partidos de los próximos días
**Uso:**
- `/proximos` → Próximos 7 días (default)
- `/proximos 3` → Próximos 3 días
- `/proximos 14` → Próximas 2 semanas

**Fuentes:** API-Football, FBref
**Con APIs configuradas:** Mucha más información y partidos
**Respuesta:**
```
⚽ PARTIDOS PRÓXIMOS (7 días)

📅 28/03/2026 - Viernes

🏆 Premier League
🏠 Manchester City vs Liverpool 🚗
🕐 20:00
🔥 Over 2.5 goles (85%)

📅 29/03/2026 - Sábado

🏆 La Liga
🏠 Real Madrid vs Barcelona 🚗
🕐 21:00
✅ BTTS (78%)
```

---

### `/partido [equipo1] vs [equipo2]`
**Descripción:** Predicción detallada de un partido específico
**Uso:** `/partido Manchester City vs Liverpool`
**Fuentes:** FBref, Understat, API-Football, The Odds API
**Respuesta:**
```
⚽ Manchester City vs Liverpool

📊 Predicciones:

🔥 Over 2.5 goles (85%)
   └ Se esperan más de 2.5 goles
   └ Razón: Promedio combinado: 3.2 goles

✅ BTTS (78%)
   └ Ambos equipos anotarán
   └ Razón: BTTS en 76% de partidos

💰 Cuotas (si Odds API activa):
   🏠 Local: 2.10
   ➖ Empate: 3.40
   🚗 Visitante: 3.20

🎯 Value Bet: [Si aplica]
```

---

### `/analizar [equipo]`
**Descripción:** Análisis completo de un equipo
**Uso:** `/analizar Real Madrid`
**Fuentes:** FBref, Understat, FotMob (opcional)
**Respuesta:**
```
📊 Análisis de Real Madrid

📈 Últimos 10 partidos:

🎯 Resultados:
✅ Victorias: 7
➖ Empates: 2
❌ Derrotas: 1

⚽ Goles:
📤 Promedio anotados: 2.8
📥 Promedio recibidos: 0.9
🧤 Valla invicta: 40%

📊 Tendencias:
🎲 BTTS: 60%
🔺 Over 2.5: 80%
🔻 Over 3.5: 50%

💡 Recomendación: Bueno para Over 2.5 goles
```

---

## 🌍 Comandos de Selecciones Nacionales

### `/selecciones [país1] vs [país2]` 🆕
**Descripción:** Predicción de partido de selecciones
**Uso:** `/selecciones Argentina vs Brasil`
**Soporta:** Amistosos, Eliminatorias, Copa América, Mundial
**Respuesta:**
```
🌍 Argentina vs Brasil
🏆 Amistoso Internacional

📊 Predicciones:

✅ Over 2.5 goles (68%)
   └ Los amistosos suelen ser más abiertos
   └ Razón: Menos presión, juego ofensivo

⚠️ Nota: Datos de selecciones limitados
Para Mundial 2026 tendremos análisis completo
```

**Selecciones disponibles:**
- 🇦🇷 Argentina, 🇧🇷 Brasil, 🇺🇾 Uruguay, 🇨🇴 Colombia
- 🇫🇷 Francia, 🇪🇸 España, 🇩🇪 Alemania, 🇮🇹 Italia
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Inglaterra, 🇵🇹 Portugal, 🇧🇪 Bélgica, 🇳🇱 Holanda
- Y más...

---

### `/mundial` 🆕
**Descripción:** Información sobre Copa del Mundo 2026
**Uso:** `/mundial`
**Respuesta:**
```
🏆 COPA DEL MUNDO FIFA 2026

📅 Fechas: 11 Junio - 19 Julio 2026

🌎 Sedes:
• 🇺🇸 Estados Unidos (11 ciudades)
• 🇲🇽 México (3 ciudades)
• 🇨🇦 Canadá (2 ciudades)

⚽ Formato:
• 48 selecciones (primera vez)
• 16 grupos de 3 equipos
• 104 partidos totales

🎯 El bot tendrá análisis especial
```

---

## 📊 Comandos de Información

### `/tendencias`
**Descripción:** Ver patrones estadísticos más confiables
**Uso:** `/tendencias`
**Respuesta:**
```
📈 PATRONES MÁS CONFIABLES

🔥 Over 2.5 en partidos top (78%)
   └ Cuando equipos del top 6 se enfrentan
   └ Aplica a: Premier League, La Liga

✅ BTTS en derbis (82%)
   └ Ambos marcan en rivalidades locales
   └ Aplica a: Todas las ligas
```

---

### `/stats`
**Descripción:** Estadísticas de precisión del bot
**Uso:** `/stats`
**Respuesta:**
```
📊 ESTADÍSTICAS DEL BOT

📅 Últimos 30 días:

📈 Predicciones totales: 150
✅ Verificadas: 120
🎯 Correctas: 95
📊 Precisión: 79.2%

🎲 Por tipo:
• Over 2.5: 85% (42/49)
• BTTS: 76% (38/50)
• Victoria local: 71% (15/21)
```

---

### `/ligas`
**Descripción:** Ver todas las ligas disponibles
**Uso:** `/ligas`
**Respuesta:**
```
🏆 LIGAS DISPONIBLES

🇪🇸 La Liga
🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
🇩🇪 Bundesliga
🇮🇹 Serie A
🇫🇷 Ligue 1
🇦🇷 Liga Profesional Argentina
```

---

## ⚙️ Comandos de Configuración

### `/suscribir`
**Descripción:** Activar/desactivar notificaciones automáticas
**Uso:** `/suscribir`
**Respuesta:**
```
✅ Suscripción activada!
Recibirás notificaciones diarias con predicciones

O

❌ Suscripción desactivada
Ya no recibirás notificaciones automáticas
```

**Notificaciones incluyen:**
- Predicciones diarias (hora configurable en .env)
- Resumen semanal (domingos)
- Partidos importantes del día

---

## 🎯 Ejemplos de Uso Completo

### Flujo típico para un partido:

**1. Ver partidos disponibles:**
```
/proximos 3
```

**2. Elegir un partido interesante:**
```
/partido Real Madrid vs Barcelona
```

**3. Analizar equipos individualmente:**
```
/analizar Real Madrid
/analizar Barcelona
```

**4. Consultar patrones:**
```
/tendencias
```

**5. Ver precisión del bot:**
```
/stats
```

---

## 💰 Value Bets (Con Odds API)

Cuando tenés The Odds API configurada (✅ YA LO TENÉS), el bot automáticamente:

1. **Obtiene cuotas** de casas de apuestas
2. **Calcula probabilidades** basadas en datos
3. **Detecta value bets** cuando:
   - Probabilidad predicha > Probabilidad implícita de las odds
4. **Recomienda** si apostar o no

**Ejemplo de análisis con value:**
```
/partido Manchester City vs Liverpool

💰 Cuotas (Bet365):
   🏠 Manchester City: 1.80
   ➖ Empate: 3.50
   🚗 Liverpool: 4.20

🎯 Value Bet Detectado:
   Manchester City gana @ 1.80

   📊 Análisis:
   • Probabilidad predicha: 65%
   • Probabilidad implícita: 55%
   • Valor esperado: +10%

   ✅ RECOMENDACIÓN: APOSTAR
```

---

## 🔄 Notificaciones Automáticas

### Configuración en `.env`:
```env
NOTIFICATION_TIME=09:00
NOTIFICATION_TIMEZONE=America/Argentina/Buenos_Aires
MIN_CONFIDENCE=70
```

### ¿Qué recibirás automáticamente?

**1. Predicciones Diarias (09:00 AM):**
```
🔥 PREDICCIONES DEL DÍA
📅 28/03/2026

Top 5 apuestas con mayor confianza:

1. 🔥 Manchester City vs Liverpool
   🎯 Over 2.5 goles
   📊 85% confianza

2. ✅ Real Madrid vs Barcelona
   🎯 BTTS
   📊 78% confianza
```

**2. Resumen Semanal (Domingos 20:00):**
```
📊 RESUMEN SEMANAL

Última semana:
📈 15 predicciones
✅ 12 correctas
📊 80% precisión

🔥 Mejor racha: Over 2.5 (90%)
```

---

## 📱 Resumen de Todos los Comandos

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Iniciar bot | `/start` |
| `/help` | Ver ayuda | `/help` |
| `/hoy` | Partidos de hoy | `/hoy` |
| **`/proximos`** | **Próximos 7 días** | **`/proximos`** |
| **`/proximos 3`** | **Próximos 3 días** | **`/proximos 3`** |
| `/partido` | Predicción de partido | `/partido Real Madrid vs Barcelona` |
| `/analizar` | Análisis de equipo | `/analizar Manchester City` |
| **`/selecciones`** | **Predicción selecciones** | **`/selecciones Argentina vs Brasil`** |
| **`/mundial`** | **Info Mundial 2026** | **`/mundial`** |
| `/tendencias` | Patrones confiables | `/tendencias` |
| `/stats` | Precisión del bot | `/stats` |
| `/ligas` | Ver ligas | `/ligas` |
| `/suscribir` | Toggle notificaciones | `/suscribir` |

**Total:** 13 comandos disponibles

---

## 🚀 Orden Recomendado para Probar

### Primera vez:
1. `/start` - Para ver bienvenida
2. `/help` - Para ver comandos
3. `/hoy` - Ver partidos de hoy
4. `/proximos` - Ver próximos partidos
5. `/partido [equipo1] vs [equipo2]` - Predicción específica

### Explorar más:
6. `/analizar [equipo]` - Análisis profundo
7. `/selecciones Argentina vs Brasil` - Probar selecciones
8. `/tendencias` - Ver patrones
9. `/stats` - Ver precisión
10. `/suscribir` - Activar notificaciones

---

## ✅ Confirmación Final

**APIs configuradas correctamente:**
- ✅ API-Football: `3201688d6cc003ea8445d01e0dcd952b`
- ✅ The Odds API: `e6a1deaad1ead644f03dec0e700265d9`
- ✅ Football-Data.org: `508c963707a644ffa0bd41506fc3bd8f`

**Todo listo para ejecutar:**
```bash
cd "C:\Users\Fer 1\soccer-betting-bot"
python main.py
```

Selecciona opción **3** (Bot + Notificaciones)

---

## 🎉 ¡El bot está listo con análisis profesional!

Con las APIs configuradas tenés:
- ✅ Partidos de los próximos 14 días
- ✅ Cuotas de casas de apuestas
- ✅ Value bets automáticos
- ✅ Análisis de 6 fuentes de datos
- ✅ Predicciones más precisas
- ✅ Selecciones nacionales
- ✅ Info del Mundial 2026

**¡A probarlo!** 🚀⚽🔥
