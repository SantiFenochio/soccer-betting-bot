# 🚀 Sistema de Scoring V2.0 - Expansión Multi-Factorial

## 📊 De 5 a 10 Factores (100 → 150 puntos)

### **FACTORES ACTUALES (Mantener)**

#### Factor 1: Base Confidence (25 pts) ⬇️ -5
```python
# Predicción del modelo principal
if confidence >= 90: score = 25
elif confidence >= 80: score = 22
elif confidence >= 75: score = 18
elif confidence >= 70: score = 15
else: score = 10
```

#### Factor 2: Form/Momentum (15 pts) ⬇️ -5
```python
# Últimos 5 partidos
points_per_game = team_points_last_5 / 5
if ppg >= 2.5: score = 15
elif ppg >= 2.0: score = 12
elif ppg >= 1.5: score = 9
else: score = 5
```

#### Factor 3: Expected Goals xG (15 pts) ⬇️ -5
```python
# Datos reales de Understat
xg_differential = team_xg - opponent_xg
if abs(xg_differential) >= 1.5: score = 15
elif abs(xg_differential) >= 1.0: score = 12
elif abs(xg_differential) >= 0.5: score = 9
else: score = 5
```

#### Factor 4: Head-to-Head (10 pts) ⬇️ -5
```python
# Últimos 5 enfrentamientos
h2h_pattern_strength = analyze_last_5_h2h()
if strong_pattern >= 4/5: score = 10
elif medium_pattern >= 3/5: score = 7
elif weak_pattern >= 2/5: score = 4
else: score = 2
```

#### Factor 5: Expected Value (15 pts) = Mantener
```python
# EV calculation con odds reales
ev_percentage = (probability * odds) - 1
if ev >= 0.15: score = 15  # 15%+ EV
elif ev >= 0.10: score = 12
elif ev >= 0.05: score = 9
elif ev >= 0.02: score = 6
else: score = 0
```

**Subtotal Actuales:** 80 puntos (antes 100)

---

### **FACTORES NUEVOS (Agregar)**

#### Factor 6: Home/Away Form Split (10 pts) 🆕 FÁCIL
```python
# Rendimiento diferencial local vs visitante
home_advantage = (home_ppg_home - away_ppg_away)

if home_advantage >= 1.5: score = 10  # Home muy superior
elif home_advantage >= 1.0: score = 8
elif home_advantage >= 0.5: score = 6
elif home_advantage >= 0: score = 4
else: score = 2  # Away superior

# Datos necesarios:
# - home_team: puntos por partido de local (últimos 5 local)
# - away_team: puntos por partido de visitante (últimos 5 visitante)
```

**Por qué importa:** Equipos como Atlético Madrid son bestias en casa pero flojos de visitante. Este factor captura eso.

---

#### Factor 7: Rest Days & Fatigue (10 pts) 🆕 FÁCIL
```python
# Días de descanso desde último partido
home_rest_days = days_since_last_match(home_team)
away_rest_days = days_since_last_match(away_team)
rest_differential = home_rest_days - away_rest_days

if abs(rest_differential) >= 5: score = 10  # Gran ventaja
elif abs(rest_differential) >= 3: score = 7
elif abs(rest_differential) >= 2: score = 5
else: score = 3  # Parejo

# Extra: Penalizar si juegan cada 3 días (Champions + Liga)
if home_rest_days <= 3: score -= 2
if away_rest_days <= 3: score -= 2

# Datos necesarios:
# - Fecha del último partido de cada equipo
# - Fixture congestion (partidos en últimos 10 días)
```

**Por qué importa:** BetQL y Action Network usan esto. Equipos cansados = más goles concedidos, menos rendimiento.

---

#### Factor 8: Injury Impact Score (15 pts) 🆕 MEDIO
```python
# Impacto de lesiones en el lineup
home_injuries = get_injured_players(home_team)
away_injuries = get_injured_players(away_team)

# Calcular impacto según importancia del jugador
home_impact = sum([player.importance * player.injury_severity for player in home_injuries])
away_impact = sum([player.importance * player.injury_severity for player in away_injuries])

impact_differential = away_impact - home_impact  # Positivo = ventaja home

if impact_differential >= 3.0: score = 15  # Away muy debilitado
elif impact_differential >= 2.0: score = 12
elif impact_differential >= 1.0: score = 9
elif impact_differential >= 0: score = 7
elif impact_differential >= -1.0: score = 5
else: score = 2  # Home muy debilitado

# Datos necesarios:
# - injury-report-tracker skill (ya existe!)
# - Importance rating: portero=10, defensa=7, mediocampo=8, delantero=9
# - Severity: minor=0.3, doubt=0.6, out=1.0
```

**Por qué importa:** Salah lesionado = Liverpool pierde 30% de su ataque. Los competidores premium integran esto.

---

#### Factor 9: Motivation & Context (10 pts) 🆕 MEDIO
```python
# Contexto del partido (importancia)
motivation_score = 0

# Posición en tabla
home_position = get_table_position(home_team)
away_position = get_table_position(away_team)

# Situaciones de alta motivación
if home_position <= 4:  # Top 4 = Champions
    motivation_score += 3
if home_position >= 17:  # Zona de descenso
    motivation_score += 5

if away_position <= 4:
    motivation_score += 3
if away_position >= 17:
    motivation_score += 5

# Derby / Clásico
if is_rivalry_match(home_team, away_team):
    motivation_score += 4

# Racha negativa larga (presión)
if home_team.losses_streak >= 3:
    motivation_score += 2
if away_team.losses_streak >= 3:
    motivation_score += 2

# Final score
score = min(motivation_score, 10)

# Datos necesarios:
# - Tabla de posiciones actual
# - Lista de rivalries/derbies
# - Rachas actuales
```

**Por qué importa:** Liverpool vs Everton (derby) tiene más intensidad que Liverpool vs Crystal Palace. Context matters.

---

#### Factor 10: Market Timing & Line Movement (10 pts) 🆕 DIFÍCIL
```python
# Movimiento de línea (sharp money indicator)
opening_odds = get_opening_odds(match)
current_odds = get_current_odds(match)

line_movement = (current_odds - opening_odds) / opening_odds

# Reverse Line Movement (RLM) = Sharp money
public_bets_percentage = get_public_betting_percentage(match)

if line_movement < -0.05 and public_bets_percentage > 60:
    # Línea bajó PERO público apuesta masivamente = Sharp money contraria
    score = 10  # ¡RLM detectado! Muy valioso
elif line_movement < -0.03:
    score = 7  # Movimiento significativo
elif line_movement < -0.01:
    score = 5  # Movimiento leve
else:
    score = 3  # No hay movimiento relevante

# Datos necesarios:
# - Histórico de odds (cada 1-2 horas)
# - Public betting percentages (de The Odds API o similar)
```

**Por qué importa:** Esto es EL SANTO GRIAL. Action Network y OddsJam cobran $200/mes solo por esto. Es el factor #1 que falta.

---

### **BONUS DE CONSISTENCIA (+10 pts)**

```python
# Bonus cuando múltiples factores coinciden
high_scores = count(factors where score >= threshold)

if high_scores >= 6:  # 6+ factores altos (de 10)
    bonus = +10
elif high_scores >= 5:
    bonus = +7
elif high_scores >= 4:
    bonus = +5
else:
    bonus = 0

total_score = sum(all_factors) + bonus
total_score = min(total_score, 150)  # Cap at 150
```

---

## 🎯 SCORING TOTAL

**Máximo:** 160 puntos (capped at 150)

**Distribución:**
- Factores originales (ajustados): 80 pts
- Factores nuevos: 55 pts
- Bonus de consistencia: 10 pts
- **Total:** 145 pts base + 10 bonus = 155 → capped at 150

---

## ⭐ NUEVO SISTEMA DE RATING

```python
def assign_stars(total_score):
    if total_score >= 135: return "⭐⭐⭐⭐⭐"  # 90%+ de 150
    elif total_score >= 120: return "⭐⭐⭐⭐"   # 80%+ de 150
    elif total_score >= 105: return "⭐⭐⭐"     # 70%+ de 150
    elif total_score >= 90: return "⭐⭐"       # 60%+ de 150
    else: return "⭐"                           # <60%
```

**Nuevo threshold recomendado:** 105 puntos (70% de 150) para aparecer en TOP 3

---

## 📊 PRIORIDAD DE IMPLEMENTACIÓN

### **FASE 1: Quick Wins (2-3 horas)** ✅ AHORA

1. **Home/Away Form Split** - Datos ya disponibles
2. **Rest Days & Fatigue** - Solo calcular días
3. **Motivation & Context** - Tabla + rivalries

**Impacto esperado:** +15-20% mejor detección de value

### **FASE 2: Medium Effort (4-6 horas)** 🔜 ESTA SEMANA

4. **Injury Impact Score** - Skill ya existe, solo integrar
5. **Weather Impact** (bonus opcional)

**Impacto esperado:** +10-15% adicional

### **FASE 3: Advanced (8+ horas)** 🔮 PRÓXIMO MES

6. **Market Timing & Line Movement** - Requiere:
   - Histórico de odds (guardar cada hora)
   - Public betting percentages API
   - Algoritmo de detección RLM

**Impacto esperado:** +20-30% (GAME CHANGER)

---

## 💡 DATOS NECESARIOS POR FACTOR

| Factor | Datos Necesarios | Fuente | Dificultad |
|--------|------------------|--------|------------|
| Home/Away Split | PPG local/visitante | API-Football | 🟢 Fácil |
| Rest Days | Fecha último partido | API-Football | 🟢 Fácil |
| Injury Impact | Lista lesionados + ratings | injury-report-tracker | 🟡 Media |
| Motivation | Tabla + rivalries | API-Football + manual | 🟡 Media |
| Line Movement | Histórico odds + public % | The Odds API + histórico | 🔴 Difícil |

---

## 🧪 EJEMPLO DE SCORING V2.0

### Partido: Manchester City vs Liverpool

```yaml
Factor 1 - Base Confidence: 22/25
  Predicción: 85% City victoria

Factor 2 - Form/Momentum: 12/15
  City: 2.8 PPG últimos 5
  Liverpool: 2.4 PPG últimos 5

Factor 3 - Expected Goals xG: 12/15
  City xG: 2.3
  Liverpool xG: 1.8
  Diferencial: +0.5

Factor 4 - Head-to-Head: 7/10
  Últimos 5: City 2-2-1 Liverpool
  Patrón medio

Factor 5 - Expected Value: 9/15
  EV: +7.5% (bueno)

Factor 6 - Home/Away Split: 8/10 🆕
  City local: 2.9 PPG
  Liverpool visitante: 2.2 PPG
  Diferencial: +0.7 (City ventaja)

Factor 7 - Rest Days: 5/10 🆕
  City: 4 días descanso
  Liverpool: 3 días descanso
  Diferencial: +1 (parejo)

Factor 8 - Injury Impact: 12/15 🆕
  City: 0 bajas importantes
  Liverpool: Salah duda (impacto -2.7)
  Ventaja: City (+2.7)

Factor 9 - Motivation: 7/10 🆕
  City: Top 4 (Champions en juego) +3
  Liverpool: Top 4 también +3
  Rivalry: +4
  Score: 7/10

Factor 10 - Line Movement: 7/10 🆕
  Opening: 1.75
  Current: 1.68 (-4% movement)
  Public: 65% en City
  Leve RLM: 7/10

━━━━━━━━━━━━━━━━━━━━━━━━━━

SUBTOTAL: 101/150

Bonus de Consistencia: +7
  (5 factores con score alto)

━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL: 108/150 ⭐⭐⭐

RECOMENDACIÓN: ✅ APOSTAR
Victoria Manchester City
Confianza: 72%
```

---

## 🚀 BENEFICIOS DEL SISTEMA V2.0

### Más Precisión
- **Antes:** 5 factores, 60-70% accuracy
- **Después:** 10 factores, 70-80% accuracy esperada

### Mejor Value Detection
- Captura contextos que el mercado ignora
- Fatiga, lesiones, motivación = edge real
- Line movement = sigue al dinero inteligente

### Menos Falsos Positivos
- Con 10 factores, un partido "malo" no puede tener score alto
- Más validación cruzada
- Bonus solo si múltiples factores coinciden

### Competitive Edge
- Injury Impact = Feature premium de competidores
- Line Movement = $200/mes feature
- Home/Away Split = Standard en top apps

---

## 📝 CONCLUSIÓN

**Sistema V2.0 expande de 5 a 10 factores:**
- ✅ 3 factores fáciles (Fase 1)
- ✅ 1 factor medio (Fase 2)
- ✅ 1 factor avanzado (Fase 3)

**Impacto total esperado:** +40-60% mejor detección de value

**ROI esperado:** Pasar de 67-75% win rate a 75-85% win rate

---

**¿Implementamos la Fase 1 ahora mismo?** 🚀
