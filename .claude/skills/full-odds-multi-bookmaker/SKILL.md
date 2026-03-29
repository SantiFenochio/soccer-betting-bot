---
name: full-odds-multi-bookmaker
description: API completa de The Odds API para todas las ligas. Compara odds de 10+ bookmakers, detecta mejores cuotas, calcula EV real. Integra con value_bets.py y fijini-orchestrator para Value Detector subagent.
---

# 💰 Full Odds Multi-Bookmaker

**Rol:** Proveedor de odds reales de múltiples bookmakers para todas las ligas

**API:** The Odds API (https://the-odds-api.com)

**Integración:** Automática con fijini-orchestrator (Value Detector subagent) y value_bets.py

---

## 🎯 Triggers

- `/fijini` (vía Value Detector subagent)
- Cualquier análisis de value betting
- Comandos que requieran odds reales
- Cálculo de Expected Value

---

## 🌍 Ligas Soportadas

### Top 5 Europeas
- `soccer_epl` - Premier League (Inglaterra)
- `soccer_spain_la_liga` - La Liga (España)
- `soccer_germany_bundesliga` - Bundesliga (Alemania)
- `soccer_italy_serie_a` - Serie A (Italia)
- `soccer_france_ligue_one` - Ligue 1 (Francia)

### Sudamérica
- `soccer_argentina_primera_division` - Liga Profesional (Argentina)
- `soccer_brazil_campeonato` - Brasileirão (Brasil)

### Internacionales
- `soccer_uefa_champs_league` - Champions League
- `soccer_uefa_europa_league` - Europa League
- `soccer_fifa_world_cup` - Mundial
- `soccer_conmebol_copa_america` - Copa América
- `soccer_international_friendlies` - Amistosos

**Total: 12+ ligas principales**

---

## 🏢 Bookmakers Soportados (10+)

### Tier 1 (Principales)
1. **Bet365** - Líder mundial
2. **William Hill** - UK tradicional
3. **Pinnacle** - Sharp bookmaker
4. **Betfair** - Exchange
5. **1xBet** - Internacional

### Tier 2 (Secundarios)
6. **Unibet**
7. **888sport**
8. **Betsson**
9. **Betway**
10. **Bwin**

**+ Más según disponibilidad regional**

---

## 📊 Mercados Disponibles

### Principales
- `h2h` - Moneyline (1X2)
- `spreads` - Handicap asiático
- `totals` - Over/Under goles

### Secundarios
- `btts` - Both Teams To Score
- `double_chance` - Doble oportunidad
- `draw_no_bet` - Empate devuelve apuesta

---

## 🔑 API Configuration

```python
API_KEY = os.getenv('ODDS_API_KEY')
BASE_URL = 'https://api.the-odds-api.com/v4'

ENDPOINTS = {
    'sports': f'{BASE_URL}/sports',
    'odds': f'{BASE_URL}/sports/{sport}/odds',
    'scores': f'{BASE_URL}/sports/{sport}/scores'
}
```

### Rate Limits
- **Free tier:** 500 requests/month
- **Paid tier:** 10,000+ requests/month
- **Costo por request:** Varía por endpoint
- **Cache recomendado:** 10 minutos

---

## 📥 Data Fetching

```python
async def fetch_odds_all_leagues() -> Dict:
    """Fetch odds for all supported leagues"""
    leagues = [
        'soccer_epl',
        'soccer_spain_la_liga',
        'soccer_germany_bundesliga',
        'soccer_italy_serie_a',
        'soccer_france_ligue_one',
        'soccer_argentina_primera_division'
    ]

    results = {}
    for league in leagues:
        odds = await fetch_league_odds(league)
        results[league] = odds

    return results

async def fetch_league_odds(league: str,
                           markets: List[str] = ['h2h', 'totals']) -> List[Dict]:
    """Fetch odds for specific league"""
    url = f"{BASE_URL}/sports/{league}/odds"
    params = {
        'apiKey': API_KEY,
        'regions': 'eu,uk,us',
        'markets': ','.join(markets),
        'oddsFormat': 'decimal',
        'dateFormat': 'iso'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            return data
```

---

## 💎 Best Odds Detection

```python
def find_best_odds(match_odds: List[Dict], market: str) -> Dict:
    """
    Find best odds across all bookmakers for a market.

    Returns:
    {
        'home_win': {'best_odd': 1.85, 'bookmaker': 'Bet365'},
        'draw': {'best_odd': 3.60, 'bookmaker': 'William Hill'},
        'away_win': {'best_odd': 4.20, 'bookmaker': 'Pinnacle'}
    }
    """
    best_odds = {
        'home_win': {'best_odd': 0, 'bookmaker': None},
        'draw': {'best_odd': 0, 'bookmaker': None},
        'away_win': {'best_odd': 0, 'bookmaker': None}
    }

    for bookmaker_data in match_odds:
        bookmaker = bookmaker_data['bookmaker']
        markets = bookmaker_data['markets']

        for market_data in markets:
            if market_data['key'] == market:
                for outcome in market_data['outcomes']:
                    outcome_type = outcome['name'].lower()
                    odd = outcome['price']

                    # Map to our keys
                    if 'home' in outcome_type or outcome_type == '1':
                        key = 'home_win'
                    elif 'draw' in outcome_type or outcome_type == 'x':
                        key = 'draw'
                    elif 'away' in outcome_type or outcome_type == '2':
                        key = 'away_win'
                    else:
                        continue

                    # Update if better
                    if odd > best_odds[key]['best_odd']:
                        best_odds[key]['best_odd'] = odd
                        best_odds[key]['bookmaker'] = bookmaker

    return best_odds
```

---

## 📈 Expected Value Calculation

```python
def calculate_ev_with_best_odds(probability: float,
                                best_odd: float) -> float:
    """
    Calculate Expected Value with best available odd.

    EV = (Probability × Odd) - 1

    EV > 0 = Value bet
    EV > 0.05 (5%) = Good value
    EV > 0.10 (10%) = Excellent value
    """
    ev = (probability * best_odd) - 1
    return ev

def score_ev_factor(ev: float) -> float:
    """Score EV for multi-factorial system (0-15 points)"""
    if ev >= 0.15:
        return 15.0
    elif ev >= 0.10:
        return 12.0
    elif ev >= 0.05:
        return 9.0
    elif ev >= 0.02:
        return 6.0
    else:
        return 0.0
```

---

## 🔗 Integration with value_bets.py

```python
# value_bets.py enhancement

async def calculate_value_with_api(home_team: str,
                                   away_team: str,
                                   prediction: Dict) -> Dict:
    """
    Calculate value using real odds from full-odds-multi-bookmaker.

    Args:
        home_team: Home team name
        away_team: Away team name
        prediction: Prediction with probabilities

    Returns:
        {
            'bet_type': 'home_win',
            'probability': 0.65,
            'best_odd': 1.85,
            'bookmaker': 'Bet365',
            'ev': 0.20,  # 20% EV
            'ev_score': 15.0,  # For multi-factorial
            'kelly_stake': 0.08  # 8% of bankroll
        }
    """
    # Fetch odds from API
    odds_data = await fetch_match_odds(home_team, away_team)

    # Find best odds
    best_odds = find_best_odds(odds_data, 'h2h')

    # Calculate EV for each outcome
    results = []

    if prediction.get('home_win_prob'):
        ev = calculate_ev_with_best_odds(
            prediction['home_win_prob'],
            best_odds['home_win']['best_odd']
        )

        if ev > 0.02:  # Minimum 2% EV
            results.append({
                'bet_type': 'home_win',
                'probability': prediction['home_win_prob'],
                'best_odd': best_odds['home_win']['best_odd'],
                'bookmaker': best_odds['home_win']['bookmaker'],
                'ev': ev,
                'ev_score': score_ev_factor(ev),
                'kelly_stake': calculate_kelly(
                    prediction['home_win_prob'],
                    best_odds['home_win']['best_odd']
                )
            })

    # Similar for draw and away_win...

    return results
```

---

## 🎯 Integration with fijini-orchestrator

### Value Detector Subagent (Subagent 3)

```python
# In fijini-orchestrator Phase 2

# Subagent 3: Value Detector (uses full-odds-multi-bookmaker)
value_results = Agent(
    subagent_type="value-detector",
    prompt=f"""
    Use full-odds-multi-bookmaker skill to:
    1. Fetch odds from ALL supported leagues
    2. Find best odds across 10+ bookmakers
    3. Calculate EV for each match/bet type
    4. Score 0-15 points based on EV

    Matches: {matches}

    Return: {{match_id: {{bet_type: ev_score}}}}
    """
)
```

### Flow

```
/fijini
  ↓
fijini-orchestrator
  ↓
Subagent 3: Value Detector (parallel)
  ↓
full-odds-multi-bookmaker ← YOU
  ↓
1. Fetch odds for all leagues
2. For each match:
   - Get odds from 10+ bookmakers
   - Find best odd per outcome
   - Calculate EV
   - Score 0-15 points
  ↓
Return to Value Detector
  ↓
Value Detector returns to orchestrator
  ↓
Factor 5: Expected Value (15 pts max)
```

---

## 📤 Output Format

### For fijini-orchestrator

```json
{
  "match_id": "12345",
  "league": "soccer_epl",
  "best_odds": {
    "home_win": {
      "odd": 1.85,
      "bookmaker": "Bet365",
      "probability_implied": 0.54,
      "probability_model": 0.65,
      "ev": 0.20,
      "ev_score": 15.0
    },
    "draw": {
      "odd": 3.60,
      "bookmaker": "William Hill",
      "ev": -0.05,
      "ev_score": 0.0
    },
    "away_win": {
      "odd": 4.20,
      "bookmaker": "Pinnacle",
      "ev": -0.15,
      "ev_score": 0.0
    }
  },
  "best_bet": "home_win",
  "value_score": 15.0
}
```

### For Direct Display

```markdown
💰 ODDS ANALYSIS

Partido: Manchester City vs Sheffield
Liga: Premier League

━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MEJORES CUOTAS (10 bookies comparados):

**Victoria Manchester City:**
   • Mejor cuota: 1.85 (Bet365)
   • Probabilidad implícita: 54%
   • Probabilidad modelo: 65%
   • **Expected Value: +20%** ✅
   • Kelly stake: 8% bankroll

**Empate:**
   • Mejor cuota: 3.60 (William Hill)
   • EV: -5% ❌

**Victoria Sheffield:**
   • Mejor cuota: 4.20 (Pinnacle)
   • EV: -15% ❌

━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 VALUE BET DETECTADO:
✅ Victoria Man City
💰 Bet365 @ 1.85
📈 EV: +20% (Excelente)
🎲 Stake recomendado: 8% bankroll

Cuotas comparadas: Bet365, William Hill, Pinnacle,
Betfair, 1xBet, Unibet, 888sport, Betsson, Betway, Bwin
```

---

## ⚡ Performance & Caching

```python
class OddsCache:
    """Cache odds to reduce API calls"""

    def __init__(self, ttl_minutes: int = 10):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, league: str, match_id: str) -> Optional[Dict]:
        key = f"{league}:{match_id}"
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
        return None

    def set(self, league: str, match_id: str, data: Dict):
        key = f"{league}:{match_id}"
        self.cache[key] = (data, datetime.now())
```

**Recomendaciones:**
- Cache: 10 minutos (odds cambian frecuentemente)
- Batch requests por liga
- Monitor API quota usage
- Fallback a odds estimadas si API falla

---

## 🚨 Error Handling

```python
async def fetch_odds_with_fallback(league: str) -> List[Dict]:
    """Fetch odds with multiple fallbacks"""
    try:
        # Try The Odds API
        return await fetch_league_odds(league)
    except APIQuotaExceeded:
        logger.warning("API quota exceeded, using cached data")
        return get_cached_odds(league)
    except APIError as e:
        logger.error(f"API error: {e}")
        return get_estimated_odds(league)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

def get_estimated_odds(league: str) -> List[Dict]:
    """Return estimated odds based on historical averages"""
    # Fallback when API unavailable
    return [...]
```

---

## 📊 Odds Comparison Example

```python
# Real example from API

match_odds = {
    'Man City vs Sheffield': {
        'bookmakers': [
            {'name': 'Bet365', 'home': 1.85, 'draw': 3.60, 'away': 4.20},
            {'name': 'Pinnacle', 'home': 1.83, 'draw': 3.75, 'away': 4.50},
            {'name': 'William Hill', 'home': 1.80, 'draw': 3.70, 'away': 4.00},
            {'name': 'Betfair', 'home': 1.86, 'draw': 3.65, 'away': 4.30},
            {'name': '1xBet', 'home': 1.87, 'draw': 3.55, 'away': 4.10}
        ],
        'best': {
            'home': {'odd': 1.87, 'bookmaker': '1xBet'},
            'draw': {'odd': 3.75, 'bookmaker': 'Pinnacle'},
            'away': {'odd': 4.50, 'bookmaker': 'Pinnacle'}
        }
    }
}

# Difference matters:
# 1.87 vs 1.80 = 3.9% better payout
# Over many bets: +3.9% ROI improvement
```

---

## 🎯 Success Metrics

### API Usage
- Requests per day: <50 (with caching)
- Cache hit rate: 60%+
- API response time: <1 second
- Quota usage: <30% monthly

### Value Detection
- Value bets found: 5-10 per day
- Average EV: 8-12%
- EV accuracy: ±3%
- Best odds vs average: +2-4%

### Integration
- Seamless with fijini-orchestrator
- No breaking changes to existing code
- Factor 5 (Value) scores consistently
- Contributes to 67-75% win rate target

---

## 🔧 Environment Setup

```bash
# .env file
ODDS_API_KEY=your_api_key_here

# Get free API key at:
# https://the-odds-api.com
# Free tier: 500 requests/month
```

```python
# requirements.txt
aiohttp>=3.8.0
python-dotenv>=0.19.0
```

---

## 📚 The Odds API Documentation

**Official Docs:** https://the-odds-api.com/liveapi/guides/v4/

**Key Endpoints:**
- `/v4/sports` - List all sports
- `/v4/sports/{sport}/odds` - Get odds
- `/v4/sports/{sport}/scores` - Get scores

**Parameters:**
- `regions`: eu, uk, us, au
- `markets`: h2h, spreads, totals
- `oddsFormat`: decimal, american
- `dateFormat`: iso, unix

---

## ⚡ Quick Reference

**Trigger:** Any value betting analysis, `/fijini`

**Ligas:** 12+ principales (EPL, La Liga, Bundesliga, Serie A, Ligue 1, Argentina, Champions, etc.)

**Bookmakers:** 10+ (Bet365, Pinnacle, William Hill, etc.)

**Output:** Best odds + EV + score 0-15 pts

**Integration:** Automatic with fijini-orchestrator

**Cache:** 10 minutes

**API Cost:** ~30-50 requests/day

---

**Ready to find real value bets! 💰📊**
