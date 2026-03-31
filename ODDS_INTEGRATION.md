# The Odds API Integration

## 🎯 Sistema de Value Bets Automático

Este sistema detecta automáticamente value bets usando:
- **football-data.org**: Datos de partidos y estadísticas de equipos
- **The Odds API**: Odds reales de múltiples bookmakers
- **Modelo Poisson**: Cálculo de probabilidades y Expected Value

## 🔧 Configuración

### Variables de entorno (.env)
```bash
# football-data.org (datos de partidos)
FOOTBALL_DATA_KEY=tu_key_aqui

# The Odds API (odds reales)
ODDS_API_KEY=tu_key_aqui
```

### APIs utilizadas

#### 1. football-data.org
- **Endpoint**: `https://api.football-data.org/v4/`
- **Uso**: Obtener partidos próximos y estadísticas de equipos
- **Rate limit**: 10 requests/minuto (free tier)

#### 2. The Odds API
- **Endpoint**: `https://api.the-odds-api.com/v4/`
- **Uso**: Obtener odds reales de bookmakers
- **Rate limit**: 500 requests/mes (free tier)
- **Ligas soportadas**:
  - `soccer_epl` (Premier League)
  - `soccer_spain_la_liga` (La Liga)
  - `soccer_germany_bundesliga` (Bundesliga)
  - `soccer_italy_serie_a` (Serie A)
  - `soccer_france_ligue_one` (Ligue 1)
  - `soccer_uefa_champs_league` (Champions League)

## 🚀 Uso

### Buscar value bets automáticamente

```python
from value_bets import ValueBetFinder

finder = ValueBetFinder()

# Buscar en Premier League
value_bets = finder.find_value_in_competition(2021)

for bet in value_bets:
    print(f"{bet['home_team']} vs {bet['away_team']}")
    print(f"Mejor apuesta: {bet['best_bet']} @ {bet['best_odds']}")
    print(f"Expected Value: +{bet['best_ev']*100:.1f}%")
    print(f"Confianza: {bet['confidence']}%")
```

### Analizar partido específico

```python
# Las odds se obtienen automáticamente de The Odds API
odds = finder.data_fetcher.get_real_odds("Arsenal", "Liverpool")

if odds:
    analysis = finder.analyze_match(
        home_team="Arsenal",
        away_team="Liverpool",
        home_odds=odds['home_win'],
        away_odds=odds['away_win'],
        draw_odds=odds['draw'],
        competition_id=2021
    )
    
    print(analysis['recommendation'])
```

## 📊 Flujo del Sistema

1. **get_upcoming_matches()**: Obtiene próximos partidos de football-data.org
2. **get_real_odds()**: Para cada partido, busca odds en The Odds API
   - Prueba múltiples ligas automáticamente
   - Usa fuzzy matching para encontrar el partido correcto
   - Retorna odds del mejor bookmaker disponible
3. **analyze_match()**: Calcula Expected Value con modelo Poisson
   - Obtiene stats reales de ambos equipos
   - Calcula probabilidades usando distribución de Poisson
   - Compara con probabilidades implícitas de las odds
   - Calcula EV = (prob_modelo × odds) - 1
4. **Filtrado**: Solo retorna partidos con EV > 5%

## 🛡️ Protección de Rate Limits

### The Odds API
- **Tracking automático**: El sistema trackea `x-requests-remaining` en cada llamada
- **Pausa automática**: Si quedan < 50 requests, se pausa la búsqueda
- **Logging**: Cada request loggea cuántos requests quedan

```python
# El sistema trackea automáticamente
finder.data_fetcher.odds_requests_remaining  # Consultar manualmente
```

### football-data.org
- **Caché**: Respuestas cacheadas por 1 hora
- **Rate limit handling**: Si recibe 429, espera 60s y reintenta una vez

## 📈 Modelo de Probabilidades

### Distribución de Poisson
Calcula probabilidades de resultados usando:

```python
λ_home = (attack_home / 100) × (defense_away / 100) × home_advantage × form
λ_away = (attack_away / 100) × (defense_home / 100) × form

P(home_win) = Σ P(home_goals > away_goals)
P(draw) = Σ P(home_goals = away_goals)
P(away_win) = Σ P(home_goals < away_goals)
```

### Expected Value
```python
EV = (probabilidad_modelo × odds_real) - 1

Si EV > 0.15: 🔥🔥🔥 EXCELENTE
Si EV > 0.10: 🔥🔥 MUY BUENO
Si EV > 0.05: 🔥 BUENO
Si EV > 0: ⚡ LEVE
Si EV < 0: ❌ SIN VALOR
```

## 🧪 Testing

```bash
# Test completo del sistema
python test_odds_integration.py

# Test individual de data_fetcher
python data_fetcher.py

# Test individual de value_bets
python value_bets.py
```

## ⚠️ Notas Importantes

1. **Free tier de The Odds API**: 500 requests/mes
   - ~16 requests/día si se distribuye uniformemente
   - Cada llamada a `find_value_in_competition()` consume 1-6 requests
   - Planifica tu uso cuidadosamente

2. **Disponibilidad de odds**: 
   - Solo disponibles para partidos próximos (generalmente 1-7 días)
   - No disponibles fuera de temporada
   - Depende de bookmakers activos en The Odds API

3. **Precisión del modelo**:
   - El modelo Poisson es una aproximación matemática
   - Las odds de bookmakers incluyen su margen
   - Value bets no garantizan ganancia (solo indican valor esperado positivo)

## 📝 Ejemplo de Output

```
🔥 TOP VALUE BETS:

1. Arsenal vs Liverpool
   📅 Fecha: 2026-04-05T15:00:00+00:00
   🎯 Recomendación: 🔥🔥 GOOD VALUE BET - HOME
   💰 Mejor apuesta: HOME @ 2.10
   📈 Expected Value: +13.07%
   ⭐ Confianza: 85%
   🏦 Bookmaker: bet365

   Probabilidades modelo (Poisson):
   • Arsenal: 53.8%
   • Empate: 28.2%
   • Liverpool: 17.6%

   Stats:
   • Arsenal: ATK 63 | DEF 90 | FORM 83
   • Liverpool: ATK 56 | DEF 54 | FORM 60
```

## 🔗 Referencias

- [football-data.org Documentation](https://www.football-data.org/documentation)
- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [Poisson Distribution in Sports Betting](https://en.wikipedia.org/wiki/Poisson_distribution#Applications)
