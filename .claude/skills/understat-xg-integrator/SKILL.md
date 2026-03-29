---
name: understat-xg-integrator
description: Obtiene datos xG reales de Understat/FBref y los integra al scoring multi-factorial. Calcula xG diferencial, sobre/underperformance, y scoring de 20 puntos para fijini-orchestrator. Datos reales, no estimados.
---

# ⚽ Understat xG Integrator

**Rol:** Proveedor de datos Expected Goals (xG) reales para análisis de apuestas

**Fuentes:** Understat.com, FBref.com (respaldo)

**Integración:** Automática con fijini-orchestrator, football-data, y xg_analyzer.py

---

## 🎯 When to Activate

**Triggers:**
- Cualquier análisis que requiera datos xG
- Comando `/xg`
- Comando `/fijini` (vía orchestrator)
- Comando `/partido` con análisis xG
- Consultas sobre "expected goals"
- Análisis de "over/under"

**Context Required:**
- Nombres de equipos (home y away)
- O ID del partido
- Fecha (opcional, default: hoy)

---

## 📊 What is xG (Expected Goals)?

### Definición
**Expected Goals (xG)** es una métrica que mide la **calidad** de las ocasiones de gol, no solo la cantidad.

- **xG = 2.3** significa que el equipo tuvo ocasiones que, históricamente, resultan en 2.3 goles
- Si marcaron **3 goles con xG 2.3** → **Overperformance** (tuvieron suerte/eficacia)
- Si marcaron **1 gol con xG 2.3** → **Underperformance** (desperdiciaron ocasiones)

### Por qué es importante para apuestas

1. **Más preciso que goles reales**
   - Un equipo puede ganar 3-0 con xG 0.8 (suerte extrema)
   - Ese resultado no es sostenible a largo plazo

2. **Predice regresión a la media**
   - Equipos con overperformance consistente → eventualmente caerán
   - Equipos con underperformance → eventualmente mejorarán

3. **Identifica value bets**
   - Mercado reacciona a goles, no a xG
   - Equipos con buen xG pero malos resultados → undervalued

---

## 🔍 Data Sources

### Primary: Understat.com

**URL:** `https://understat.com/`

**Cobertura:**
- ✅ Premier League (Inglaterra)
- ✅ La Liga (España)
- ✅ Bundesliga (Alemania)
- ✅ Serie A (Italia)
- ✅ Ligue 1 (Francia)
- ✅ RFPL (Rusia)

**Datos Disponibles:**
- xG por equipo por partido
- xG por jugador por tiro
- xG acumulado por temporada
- xG promedio últimos N partidos
- Mapas de tiros (shot maps)

**Método de Acceso:**
- Web scraping (BeautifulSoup + requests)
- No tiene API oficial pública
- Rate limit: ~1 request/segundo

### Secondary: FBref.com

**URL:** `https://fbref.com/`

**Cobertura:**
- ✅ Todas las ligas principales
- ✅ Competiciones internacionales
- ✅ Más ligas que Understat

**Datos Disponibles:**
- xG por partido
- xGA (xG Against - esperado concedido)
- xG por 90 minutos
- Estadísticas avanzadas

**Método de Acceso:**
- Web scraping
- Respaldo cuando Understat no tiene datos

---

## 📥 Data Extraction Process

### Step 1: Identify Team
```python
def normalize_team_name(team_name: str) -> str:
    """
    Normalize team name for Understat URL format.

    Examples:
    - "Manchester City" → "Manchester_City"
    - "Real Madrid" → "Real_Madrid"
    - "PSG" → "Paris_Saint_Germain"
    """
    mapping = {
        "Man City": "Manchester_City",
        "PSG": "Paris_Saint_Germain",
        "Bayern": "Bayern_Munich",
        # ... full mapping
    }
    return mapping.get(team_name, team_name.replace(" ", "_"))
```

### Step 2: Fetch xG Data
```python
async def fetch_team_xg(team: str, last_n_games: int = 5) -> Dict:
    """
    Fetch xG data for team from Understat.

    Returns:
    {
        'team': 'Manchester_City',
        'last_5_matches': [
            {'xg_for': 2.8, 'xg_against': 0.4, 'result': '3-0'},
            {'xg_for': 2.1, 'xg_against': 1.2, 'result': '2-1'},
            ...
        ],
        'avg_xg_for': 2.45,
        'avg_xg_against': 0.65,
        'overperformance': +0.3  # Scoring 0.3 more than xG
    }
    """
    url = f"https://understat.com/team/{team}/2024"
    html = await fetch_url(url)
    data = parse_xg_from_html(html)
    return calculate_xg_stats(data, last_n_games)
```

### Step 3: Calculate xG Differential
```python
def calculate_xg_differential(home_xg: Dict, away_xg: Dict) -> float:
    """
    Calculate expected goal differential for match.

    Positive = Home advantage
    Negative = Away advantage
    """
    home_attack = home_xg['avg_xg_for']
    home_defense = home_xg['avg_xg_against']
    away_attack = away_xg['avg_xg_for']
    away_defense = away_xg['avg_xg_against']

    # Expected xG for this match
    home_expected_xg = (home_attack + away_defense) / 2
    away_expected_xg = (away_attack + home_defense) / 2

    differential = home_expected_xg - away_expected_xg
    return differential
```

---

## 🎲 Scoring Integration (20 Points)

### Factor 3: Expected Goals (20 points)

Este es el componente que se integra con **fijini-orchestrator**.

```python
def score_xg_factor(home_xg: Dict, away_xg: Dict,
                    bet_type: str) -> float:
    """
    Score xG factor (0-20 points) for multi-factorial system.

    Args:
        home_xg: xG stats for home team
        away_xg: xG stats for away team
        bet_type: 'over_2.5', 'under_2.5', 'home_win', etc.

    Returns:
        Score from 0-20 points
    """
    differential = calculate_xg_differential(home_xg, away_xg)
    total_xg = home_xg['avg_xg_for'] + away_xg['avg_xg_for']

    if bet_type == 'over_2.5':
        return score_over_under(total_xg, 2.5, 'over')
    elif bet_type == 'under_2.5':
        return score_over_under(total_xg, 2.5, 'under')
    elif bet_type == 'home_win':
        return score_result(differential, 'home')
    elif bet_type == 'away_win':
        return score_result(differential, 'away')
    elif bet_type == 'btts':
        return score_btts(home_xg, away_xg)
    else:
        return 10.0  # Neutral

def score_over_under(total_xg: float, line: float,
                     direction: str) -> float:
    """Score Over/Under based on total xG"""
    if direction == 'over':
        if total_xg >= line + 1.0:
            return 20.0  # Very strong
        elif total_xg >= line + 0.5:
            return 16.0  # Strong
        elif total_xg >= line:
            return 12.0  # Moderate
        else:
            return 8.0   # Weak
    else:  # under
        if total_xg <= line - 1.0:
            return 20.0
        elif total_xg <= line - 0.5:
            return 16.0
        elif total_xg <= line:
            return 12.0
        else:
            return 8.0

def score_result(differential: float, result: str) -> float:
    """Score match result based on xG differential"""
    if result == 'home':
        if differential >= 1.5:
            return 20.0  # Huge home advantage
        elif differential >= 1.0:
            return 16.0  # Strong home advantage
        elif differential >= 0.5:
            return 12.0  # Moderate home advantage
        else:
            return 8.0   # Slight/no advantage
    else:  # away
        if differential <= -1.5:
            return 20.0
        elif differential <= -1.0:
            return 16.0
        elif differential <= -0.5:
            return 12.0
        else:
            return 8.0

def score_btts(home_xg: Dict, away_xg: Dict) -> float:
    """Score Both Teams To Score"""
    home_attack = home_xg['avg_xg_for']
    away_attack = away_xg['avg_xg_for']

    # Both teams need decent attacking xG
    min_xg = min(home_attack, away_attack)

    if min_xg >= 1.5 and home_attack + away_attack >= 3.5:
        return 20.0  # Both teams scoring well
    elif min_xg >= 1.2 and home_attack + away_attack >= 3.0:
        return 16.0
    elif min_xg >= 1.0 and home_attack + away_attack >= 2.5:
        return 12.0
    else:
        return 8.0
```

---

## 🔗 Integration with fijini-orchestrator

### Automatic Integration

El **fijini-orchestrator** llama a esta skill automáticamente cuando necesita el factor xG:

```python
# En fijini-orchestrator, Phase 2: Parallel Analysis

# Subagent 2: xG Analyzer (usa understat-xg-integrator)
xg_results = Agent(
    subagent_type="xg-analyzer",
    prompt=f"""
    Use understat-xg-integrator skill to fetch xG data for:
    {matches}

    For each match, calculate:
    - xG differential
    - Over/Under probability
    - BTTS probability
    - Result likelihood

    Return scoring (0-20 points) for each bet type.
    """
)
```

### Integration Flow

```
User: /fijini
    │
    ├─► fijini-orchestrator (Lead Agent)
        │
        ├─► Data Fetcher → Obtiene partidos
        │
        ├─► xG Analyzer (Subagent 2)
        │   │
        │   └─► understat-xg-integrator ← YOU ARE HERE
        │       │
        │       ├─► Fetch home team xG from Understat
        │       ├─► Fetch away team xG from Understat
        │       ├─► Calculate differential
        │       └─► Return 0-20 score
        │
        ├─► Value Detector (Subagent 3)
        └─► Context Analyzer (Subagent 4)
```

---

## 📤 Output Format

### For fijini-orchestrator Integration

```json
{
  "match_id": "12345",
  "home": "Manchester_City",
  "away": "Sheffield_United",
  "xg_data": {
    "home_xg_avg": 2.45,
    "away_xg_avg": 0.85,
    "home_xga_avg": 0.65,
    "away_xga_avg": 1.95,
    "differential": 1.60,
    "total_expected": 3.30
  },
  "scores": {
    "over_2.5": 18.0,
    "under_2.5": 8.0,
    "home_win": 20.0,
    "away_win": 5.0,
    "btts": 12.0
  },
  "confidence": "high",
  "notes": [
    "Home team massive xG advantage (+1.60)",
    "Total xG suggests Over 2.5 (3.30 expected)",
    "Away team weak attack (0.85 xG/game)"
  ]
}
```

### For Direct /xg Command

```markdown
⚽ **xG ANALYSIS** ⚽

**Partido:** Manchester City vs Sheffield United
**Liga:** Premier League
**Fecha:** 2026-03-29

━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **EXPECTED GOALS (xG)**

**Manchester City:**
   • xG promedio (últimos 5): 2.45
   • xG Against (últimos 5): 0.65
   • Overperformance: +0.3 goles
   • Eficiencia: Alta (123%)

**Sheffield United:**
   • xG promedio (últimos 5): 0.85
   • xG Against (últimos 5): 1.95
   • Underperformance: -0.2 goles
   • Eficiencia: Baja (76%)

━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **PREDICCIONES xG**

**Para este partido:**
   • xG esperado Manchester City: 2.05
   • xG esperado Sheffield: 0.65
   • **Diferencial: +1.40** (ventaja City)
   • **Total esperado: 2.70 goles**

**Recomendaciones basadas en xG:**
   ✅ Victoria Manchester City (20/20 pts)
   ✅ Over 2.5 goles (16/20 pts)
   ⚠️ BTTS No (12/20 pts)

━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 **INSIGHTS:**
   • City tiene ventaja xG abrumadora (+1.40)
   • Sheffield concede muchas ocasiones (1.95 xGA)
   • Partido debería tener 2-3 goles mínimo
   • Sheffield poco probable que marque (0.65 xG)

📉 **TENDENCIAS:**
   • City overperforming → sostenible
   • Sheffield underperforming → mejorarán algo
   • Pero diferencia de calidad es muy grande

⚠️ xG es estadística, no garantía.
```

---

## 🛠️ Implementation Details

### Web Scraping: Understat

```python
import aiohttp
from bs4 import BeautifulSoup
import json
import re

class UnderstatScraper:
    """Scraper for Understat.com xG data"""

    BASE_URL = "https://understat.com"

    async def get_team_xg(self, team: str, season: str = "2024") -> Dict:
        """Get team xG data for season"""
        url = f"{self.BASE_URL}/team/{team}/{season}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()

        # Parse JSON data embedded in script tag
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            if 'teamsData' in script.text:
                # Extract JSON from JavaScript
                json_str = re.search(
                    r'var teamsData = JSON.parse\(\'(.+?)\'\)',
                    script.text
                )
                if json_str:
                    data = json.loads(json_str.group(1))
                    return self.parse_team_data(data)

        raise ValueError(f"No xG data found for {team}")

    def parse_team_data(self, data: Dict) -> Dict:
        """Parse and structure team xG data"""
        matches = []

        for match in data['matches'][-5:]:  # Last 5
            matches.append({
                'xg_for': float(match['xG']),
                'xg_against': float(match['xGA']),
                'goals_for': int(match['scored']),
                'goals_against': int(match['missed']),
                'result': match['result']
            })

        return {
            'team': data['team_name'],
            'matches': matches,
            'avg_xg_for': sum(m['xg_for'] for m in matches) / len(matches),
            'avg_xg_against': sum(m['xg_against'] for m in matches) / len(matches)
        }
```

### Cache System

```python
from datetime import datetime, timedelta
import json

class XGCache:
    """Cache xG data to reduce API calls"""

    def __init__(self, cache_duration_hours: int = 6):
        self.cache = {}
        self.cache_duration = timedelta(hours=cache_duration_hours)

    def get(self, team: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        if team in self.cache:
            data, timestamp = self.cache[team]
            if datetime.now() - timestamp < self.cache_duration:
                return data
        return None

    def set(self, team: str, data: Dict):
        """Cache team xG data"""
        self.cache[team] = (data, datetime.now())

    def clear_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired = [
            team for team, (_, ts) in self.cache.items()
            if now - ts >= self.cache_duration
        ]
        for team in expired:
            del self.cache[team]
```

---

## ⚡ Performance Optimization

### Rate Limiting

```python
import asyncio

class RateLimiter:
    """Rate limiter for Understat scraping"""

    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0

    async def wait(self):
        """Wait if necessary to respect rate limit"""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_call

        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)

        self.last_call = asyncio.get_event_loop().time()
```

### Batch Processing

```python
async def fetch_multiple_teams_xg(teams: List[str]) -> Dict[str, Dict]:
    """Fetch xG for multiple teams in parallel (with rate limiting)"""
    limiter = RateLimiter(calls_per_second=1.0)
    cache = XGCache()

    results = {}

    for team in teams:
        # Check cache first
        cached = cache.get(team)
        if cached:
            results[team] = cached
            continue

        # Rate limit
        await limiter.wait()

        # Fetch
        data = await scraper.get_team_xg(team)
        cache.set(team, data)
        results[team] = data

    return results
```

---

## 🚨 Error Handling

### Fallback to FBref

```python
async def fetch_xg_with_fallback(team: str) -> Dict:
    """Fetch xG with automatic fallback to FBref"""
    try:
        # Try Understat first
        return await understat_scraper.get_team_xg(team)
    except Exception as e:
        logger.warning(f"Understat failed for {team}: {e}")

        try:
            # Fallback to FBref
            return await fbref_scraper.get_team_xg(team)
        except Exception as e2:
            logger.error(f"FBref also failed for {team}: {e2}")

            # Return default/estimated values
            return get_default_xg(team)

def get_default_xg(team: str) -> Dict:
    """Return conservative default xG values"""
    return {
        'team': team,
        'avg_xg_for': 1.3,  # League average
        'avg_xg_against': 1.3,
        'confidence': 'low',
        'source': 'default'
    }
```

### Handle Missing Data

```python
def validate_xg_data(data: Dict) -> bool:
    """Validate xG data is complete and sensible"""
    required_keys = ['avg_xg_for', 'avg_xg_against']

    # Check all keys present
    if not all(key in data for key in required_keys):
        return False

    # Check values are reasonable (0 to 5 xG per game)
    if not (0 <= data['avg_xg_for'] <= 5):
        return False
    if not (0 <= data['avg_xg_against'] <= 5):
        return False

    return True
```

---

## 📊 Testing

### Unit Tests

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_team_xg():
    """Test fetching xG for a team"""
    scraper = UnderstatScraper()
    data = await scraper.get_team_xg("Manchester_City")

    assert 'avg_xg_for' in data
    assert 'avg_xg_against' in data
    assert data['avg_xg_for'] > 0

@pytest.mark.asyncio
async def test_xg_scoring():
    """Test xG scoring function"""
    home_xg = {'avg_xg_for': 2.5, 'avg_xg_against': 0.6}
    away_xg = {'avg_xg_for': 0.8, 'avg_xg_against': 2.0}

    score = score_xg_factor(home_xg, away_xg, 'home_win')

    assert 15 <= score <= 20  # Should be high score

@pytest.mark.asyncio
async def test_cache():
    """Test caching mechanism"""
    cache = XGCache(cache_duration_hours=1)

    data = {'avg_xg_for': 2.0}
    cache.set("Test_Team", data)

    cached = cache.get("Test_Team")
    assert cached == data
```

---

## 🔍 Best Practices

### 1. **Always Use Cache**
```python
# ✅ Good
cached = cache.get(team)
if cached:
    return cached
data = await fetch_xg(team)
cache.set(team, data)

# ❌ Bad
data = await fetch_xg(team)  # No cache check
```

### 2. **Respect Rate Limits**
```python
# ✅ Good
await rate_limiter.wait()
data = await fetch_xg(team)

# ❌ Bad
for team in teams:
    await fetch_xg(team)  # Too fast
```

### 3. **Handle Errors Gracefully**
```python
# ✅ Good
try:
    return await fetch_xg(team)
except:
    return get_default_xg(team)

# ❌ Bad
return await fetch_xg(team)  # Can crash
```

### 4. **Validate Data**
```python
# ✅ Good
data = await fetch_xg(team)
if validate_xg_data(data):
    return data
else:
    return get_default_xg(team)

# ❌ Bad
return await fetch_xg(team)  # Might be corrupted
```

---

## 📚 References

**Understat.com:**
- Homepage: https://understat.com/
- xG Model: Statistical model based on shot location, type, situation
- Data: 2014-present for top 5 leagues

**FBref.com:**
- Homepage: https://fbref.com/
- Source: StatsBomb data
- Coverage: More leagues than Understat

**Academic Papers:**
- "Expected Goals in Football" (2012)
- "Assessing the Value of a Shot" (2015)
- "xG Philosophy" by James Tippett

---

## 🎯 Success Metrics

### Data Quality
- ✅ xG data available for 95%+ of matches
- ✅ Cache hit rate > 70%
- ✅ API response time < 2 seconds
- ✅ Error rate < 5%

### Scoring Accuracy
- ✅ xG factor correlates with actual results
- ✅ High xG differential → high win probability
- ✅ xG predictions better than goals-based predictions

### Integration
- ✅ Seamless integration with fijini-orchestrator
- ✅ No breaking changes to existing code
- ✅ Backward compatible with xg_analyzer.py

---

## ⚡ Quick Reference

**Trigger:** Any xG-related analysis

**Primary Source:** Understat.com (scraping)

**Fallback:** FBref.com

**Output:** 0-20 point score + detailed xG stats

**Integration:** Automatic with fijini-orchestrator

**Cache:** 6 hours

**Rate Limit:** 1 request/second

---

**Ready to integrate real xG data! ⚽📊**
