# 🔥 Fijini Orchestrator - Lead Agent

**La skill más importante del bot.** Actúa como orquestador principal del comando `/fijini`.

---

## 🎯 ¿Qué hace?

Coordina todo el análisis multi-factorial para encontrar las **TOP 3 mejores apuestas del día**.

### Arquitectura

```
┌─────────────────────────────────────────┐
│       FIJINI ORCHESTRATOR               │
│         (Lead Agent)                    │
└────────┬────────────────────────────────┘
         │
         ├─► Data Fetcher
         │   └─► Obtiene TODOS los partidos
         │
         ├─► Parallel Analysis (3 subagentes)
         │   ├─► xG Analyzer
         │   ├─► Value Detector
         │   └─► Context Analyzer
         │
         ├─► Scoring & Ranking
         │   └─► Sistema de 100 puntos
         │
         └─► Report Generator
             └─► Output profesional Telegram
```

---

## 🚀 Cómo se activa

### Automático
La skill se activa automáticamente cuando detecta:
- `/fijini`
- "mejores apuestas del día"
- "top picks de hoy"
- "locks del día"

### Manual
No es necesario llamarla manualmente. El bot la usa automáticamente.

---

## 📊 Sistema Multi-Factorial (100 puntos)

### 5 Factores de Análisis

1. **Base Confidence (30 pts)** - Predicción del modelo principal
2. **Form/Momentum (20 pts)** - Últimos 5 partidos, racha
3. **Expected Goals (20 pts)** - Datos reales xG
4. **Head-to-Head (15 pts)** - Últimos 5 enfrentamientos
5. **Expected Value (15 pts)** - Cálculo de EV

### Bonus de Consistencia (+10 pts)
Si 3 o más factores tienen score ≥15, se añaden 10 puntos bonus.

**Total máximo:** 100 puntos (110 con bonus, capped a 100)

---

## ⭐ Sistema de Rating

| Score | Estrellas | Significado |
|-------|-----------|-------------|
| 90-100 | ⭐⭐⭐⭐⭐ | Lock máximo - Apuesta con máxima confianza |
| 80-89 | ⭐⭐⭐⭐ | Muy confiable - Apuesta fuerte |
| 75-79 | ⭐⭐⭐ | Confiable - Apuesta moderada |
| 70-74 | ⭐⭐ | Moderado - No incluido en TOP 3 |
| <70 | ⭐ | Bajo - No incluido |

**Threshold:** Solo locks con ≥75 puntos (3+ estrellas) aparecen en TOP 3.

---

## 🎯 Target de Precisión

### Objetivo: 67-75% Win Rate

**Esperado por rating:**
- ⭐⭐⭐⭐⭐ (90+ pts): 75-85% win rate
- ⭐⭐⭐⭐ (80-89 pts): 65-75% win rate
- ⭐⭐⭐ (75-79 pts): 60-70% win rate

**Filosofía:** Calidad sobre cantidad. Mejor 0-2 locks que 3 locks malos.

---

## ⚡ Ejecución Paralela

### Ventaja: 3x más rápido

Los 3 subagentes de análisis corren **en paralelo**:

```python
# Serial (antigua forma): 150 segundos
xg_analysis()       # 50 seg
value_detection()   # 40 seg
context_analysis()  # 60 seg
# Total: 150 seg

# Parallel (nueva forma): 60 segundos
parallel_run([
    xg_analysis(),      # 50 seg ─┐
    value_detection(),  # 40 seg  ├─► Simultáneos
    context_analysis()  # 60 seg ─┘
])
# Total: 60 seg (el más lento)
```

**Resultado:** `/fijini` tarda ~60-90 segundos en lugar de ~2-3 minutos.

---

## 📤 Output Profesional

### Formato Telegram

El orchestrator genera output profesional con:

- ✅ Emojis estratégicos (no excesivos)
- ✅ **Texto en negrita** para énfasis
- ✅ Separadores visuales (━━━━)
- ✅ Estructura clara y escaneable
- ✅ Rating de estrellas ⭐
- ✅ Desglose de scores
- ✅ Factores clave destacados
- ✅ Disclaimer de responsabilidad

### Ejemplo

```
🔥 FIJINI - TOP 3 LOCKS DEL DÍA 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 LOCK #1 ⭐⭐⭐⭐⭐
⚽ Partido: Man City vs Sheffield
🏆 Liga: Premier League
🕐 Hora: 15:00hs

🎯 APUESTA RECOMENDADA:
   💡 Victoria Manchester City
   📊 Confianza: 92%
   🎲 Score: 94.5/100

📈 Análisis Multi-Factorial:
   • Base: 28/30
   • Forma: 20/20
   • xG: 20/20
   • H2H: 15/15
   • Value: 11/15

🔍 Factores Clave:
   ✓ Forma excepcional: 3.0 PPG
   ✓ Ventaja xG: +1.8
   ✓ H2H dominio: 100%

💭 City superior en todos los aspectos
```

---

## 🛠️ Integración con el Bot

### En bot.py

```python
# Handler ya existe
async def fijini_command(update, context):
    # El fijini-orchestrator se activa automáticamente
    # Ejecuta el análisis completo
    # Retorna TOP 3 locks formateados
```

**No requiere código adicional.** La skill se integra automáticamente con el comando existente.

---

## 📚 Archivos de la Skill

```
fijini-orchestrator/
├── SKILL.md                    # Documentación principal (13.9 KB)
├── implementation-guide.md     # Guía de implementación (19.1 KB)
└── README.md                   # Este archivo
```

### SKILL.md
Contiene:
- Arquitectura completa
- Sistema de scoring detallado
- Output format
- Error handling
- Best practices

### implementation-guide.md
Contiene:
- Código de ejemplo Python
- Implementación de subagentes
- Testing examples
- Performance monitoring
- Deployment checklist

---

## 🧪 Testing

### Escenarios de Test

1. **Día normal con buenos locks**
   - Input: `/fijini`
   - Expected: TOP 3 locks con 3-5 estrellas

2. **Día sin partidos**
   - Input: `/fijini`
   - Expected: "No se encontraron partidos"

3. **Día con locks malos**
   - Input: `/fijini`
   - Expected: "No se encontraron locks de alta calidad"

4. **Día con solo 1-2 locks buenos**
   - Input: `/fijini`
   - Expected: Retorna 1-2 locks (no fuerza 3)

---

## 🚨 Mensajes de Error

### No hay partidos
```
❌ No se encontraron partidos para hoy.
Intenta de nuevo más tarde.
```

### No hay locks de calidad
```
⚠️ No se encontraron locks de alta calidad hoy.

El análisis multi-factorial no identificó apuestas
que cumplan con los criterios de calidad (75+ puntos).

💡 Recuerda: No apostar es mejor que apostar mal.
Espera a mejores oportunidades mañana. 🎯
```

### Error de API
```
❌ Error al obtener datos. Intenta en unos minutos.
```

---

## 📊 Performance Metrics

### Monitoreables

- **Execution time:** Target < 90 segundos
- **Win rate por estrellas:** Tracking histórico
- **ROI overall:** Target +10-20%
- **User engagement:** Cuántos usan los picks

### Tracking (Opcional)

```python
# En bankroll_manager o base de datos
track_fijini_pick({
    'date': today,
    'lock_number': 1,
    'score': 94.5,
    'stars': 5,
    'result': None  # Llenar después
})
```

---

## 🎓 Best Practices

### ✅ DO:
- Confiar en locks de 4-5 estrellas
- Usar Kelly Criterion para stakes
- Combinar con `/partido` para análisis profundo
- Verificar lesiones antes de apostar
- Apostar moderadamente en 3 estrellas

### ❌ DON'T:
- Apostar ciegamente sin revisar
- Ignorar el disclaimer
- Apostar todo a un solo lock
- Forzar apuestas en días malos
- Apostar más del 5% del bankroll

---

## 🔗 Related Commands

### Workflow Recomendado

```
1. /fijini
   → Ver TOP 3 locks del día

2. /partido [equipo1] vs [equipo2]
   → Análisis detallado del lock #1

3. /xg [equipo1] vs [equipo2]
   → Confirmar con xG real

4. /h2h [equipo1] vs [equipo2]
   → Verificar historial

5. /apostar [detalles]
   → Registrar apuesta

6. /liquidar [id] [won/lost]
   → Cerrar apuesta al final
```

---

## 🆘 Troubleshooting

### La skill no se activa
1. Verificar que `/fijini` esté registrado en bot.py
2. Revisar que SKILL.md exista en `.claude/skills/fijini-orchestrator/`
3. Reiniciar el bot

### Análisis muy lento
1. Verificar que los subagentes corran en paralelo
2. Optimizar llamadas a APIs externas
3. Considerar cache para datos estáticos

### Resultados inconsistentes
1. Verificar que el sistema de scoring esté correcto
2. Revisar que el bonus de consistencia se aplique bien
3. Confirmar que el threshold de 75 pts se respete

---

## 📈 Roadmap Futuro

### Posibles Mejoras

1. **Machine Learning**
   - Entrenar modelo para ajustar pesos de factores
   - Aprender de resultados históricos

2. **Más Factores**
   - Clima y condiciones
   - Árbitro historical bias
   - Motivación (posición en tabla)

3. **Personalización**
   - Ajustar risk tolerance por usuario
   - Preferencias de tipo de apuesta

4. **Live Updates**
   - Re-análisis si hay lesiones de última hora
   - Ajuste de locks si odds cambian significativamente

---

## 🤝 Contribuir

Para mejorar la skill:

1. Editar `SKILL.md` con nuevas instrucciones
2. Actualizar `implementation-guide.md` con código
3. Testear con `/fijini`
4. Monitorear win rate
5. Iterar basado en resultados

---

## 📞 Soporte

Si tienes problemas con fijini-orchestrator:

1. Lee esta documentación completa
2. Revisa `SKILL.md` para detalles técnicos
3. Consulta `implementation-guide.md` para código
4. Testea los escenarios de error
5. Revisa los logs del bot

---

## 🎉 Conclusión

**fijini-orchestrator** es el corazón del bot. Coordina todas las skills, analiza todo el mercado, y entrega las mejores apuestas del día de forma automática y profesional.

**Filosofía:** Calidad > Cantidad. Mejor 0 locks que locks malos.

**Target:** 67-75% win rate. Realistic y sostenible.

**Velocidad:** 60-90 segundos con ejecución paralela.

**Output:** Profesional, claro, y accionable.

---

**¡Listo para encontrar los locks del día! 🔥⚽💰**

**Última actualización:** 29 de Marzo, 2026
**Versión:** 1.0
**Status:** ✅ Instalada y lista para usar
