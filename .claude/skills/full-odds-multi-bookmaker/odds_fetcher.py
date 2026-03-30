"""
Full Odds Multi-Bookmaker - Implementation
Fetches real odds from The Odds API and finds best available odds.
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv('ODDS_API_KEY', '')
BASE_URL = 'https://api.the-odds-api.com/v4'

# Supported leagues
SUPPORTED_LEAGUES = {
    'EPL': 'soccer_epl',
    'La Liga': 'soccer_spain_la_liga',
    'Bundesliga': 'soccer_germany_bundesliga',
    'Serie A': 'soccer_italy_serie_a',
    'Ligue 1': 'soccer_france_ligue_one',
    'Argentina': 'soccer_argentina_primera_division',
    'Brazil': 'soccer_brazil_campeonato',
    'Champions': 'soccer_uefa_champs_league',
    'Europa': 'soccer_uefa_europa_league',
}


class OddsCache:
    """Cache for odds data to reduce API calls"""

    def __init__(self, ttl_minutes: int = 10):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)

    def get(self, key: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
        return None

    def set(self, key: str, data: Dict):
        """Cache data with timestamp"""
        self.cache[key] = (data, datetime.now())

    def clear_expired(self):
        """Remove expired cache entries"""
        now = datetime.now()
        expired = [
            key for key, (_, ts) in self.cache.items()
            if now - ts >= self.ttl
        ]
        for key in expired:
            del self.cache[key]


class OddsAPIClient:
    """Client for The Odds API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or API_KEY
        self.cache = OddsCache(ttl_minutes=10)
        self.base_url = BASE_URL

        if not self.api_key:
            logger.warning("No ODDS_API_KEY found in environment")

    async def fetch_league_odds(
        self,
        league: str,
        markets: List[str] = None,
        regions: str = 'eu,uk,us'
    ) -> List[Dict]:
        """
        Fetch odds for a specific league.

        Args:
            league: League key (e.g., 'soccer_epl')
            markets: List of markets (default: ['h2h', 'totals'])
            regions: Regions to fetch from

        Returns:
            List of matches with odds
        """
        if markets is None:
            markets = ['h2h', 'totals', 'btts']

        # Check cache
        cache_key = f"{league}:{','.join(markets)}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {league}")
            return cached

        # Fetch from API
        url = f"{self.base_url}/sports/{league}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': regions,
            'markets': ','.join(markets),
            'oddsFormat': 'decimal',
            'dateFormat': 'iso'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.cache.set(cache_key, data)
                        logger.info(f"Fetched {len(data)} matches for {league}")
                        return data
                    elif response.status == 401:
                        logger.error("Invalid API key")
                        return []
                    elif response.status == 429:
                        logger.error("Rate limit exceeded")
                        return []
                    else:
                        logger.error(f"API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching odds: {e}")
            return []

    async def fetch_all_leagues_odds(
        self,
        leagues: List[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Fetch odds for multiple leagues in parallel.

        Args:
            leagues: List of league keys (default: all supported)

        Returns:
            Dict mapping league -> matches
        """
        if leagues is None:
            leagues = list(SUPPORTED_LEAGUES.values())

        tasks = [
            self.fetch_league_odds(league)
            for league in leagues
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            league: result if not isinstance(result, Exception) else []
            for league, result in zip(leagues, results)
        }


def find_best_odds(bookmakers_data: List[Dict], market: str) -> Dict:
    """
    Find best odds across all bookmakers for a market.

    Args:
        bookmakers_data: List of bookmaker data from API
        market: Market key ('h2h', 'totals', etc.)

    Returns:
        {
            'home_win': {'odd': 1.87, 'bookmaker': '1xBet'},
            'draw': {'odd': 3.75, 'bookmaker': 'Pinnacle'},
            'away_win': {'odd': 4.50, 'bookmaker': 'Pinnacle'},
            'over_2.5': {'odd': 2.10, 'bookmaker': 'Bet365'},
            'under_2.5': {'odd': 1.75, 'bookmaker': 'William Hill'}
        }
    """
    best_odds = {}

    for bookmaker_entry in bookmakers_data:
        bookmaker = bookmaker_entry.get('key', 'Unknown')
        markets = bookmaker_entry.get('markets', [])

        for market_data in markets:
            if market_data['key'] != market:
                continue

            for outcome in market_data['outcomes']:
                outcome_name = outcome['name']
                odd = outcome['price']

                # Map outcome to standardized key
                if market == 'h2h':
                    if outcome_name == 'Home' or 'home' in outcome_name.lower():
                        key = 'home_win'
                    elif outcome_name == 'Draw' or 'draw' in outcome_name.lower():
                        key = 'draw'
                    elif outcome_name == 'Away' or 'away' in outcome_name.lower():
                        key = 'away_win'
                    else:
                        continue

                elif market == 'totals':
                    if outcome_name == 'Over':
                        key = 'over_2.5'
                    elif outcome_name == 'Under':
                        key = 'under_2.5'
                    else:
                        continue

                elif market == 'btts':
                    if outcome_name == 'Yes':
                        key = 'btts_yes'
                    elif outcome_name == 'No':
                        key = 'btts_no'
                    else:
                        continue

                else:
                    continue

                # Update if better odd
                if key not in best_odds or odd > best_odds[key]['odd']:
                    best_odds[key] = {
                        'odd': odd,
                        'bookmaker': bookmaker
                    }

    return best_odds


def calculate_ev(probability: float, odd: float) -> float:
    """
    Calculate Expected Value.

    EV = (Probability × Odd) - 1

    Args:
        probability: Model probability (0-1)
        odd: Decimal odd

    Returns:
        EV as decimal (0.10 = 10% EV)
    """
    return (probability * odd) - 1


def score_ev_factor(ev: float) -> float:
    """
    Score EV for multi-factorial system (0-15 points).

    Args:
        ev: Expected Value

    Returns:
        Score from 0-15
    """
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


def calculate_kelly_stake(
    probability: float,
    odd: float,
    bankroll: float = 1000,
    fraction: float = 0.25
) -> float:
    """
    Calculate Kelly Criterion stake.

    Kelly = (bp - q) / b
    Where:
        b = decimal odds - 1
        p = probability
        q = 1 - p

    Args:
        probability: Win probability
        odd: Decimal odd
        bankroll: Total bankroll
        fraction: Fractional Kelly (0.25 = quarter Kelly)

    Returns:
        Recommended stake amount
    """
    b = odd - 1
    p = probability
    q = 1 - p

    kelly = (b * p - q) / b

    if kelly <= 0:
        return 0.0

    stake = kelly * fraction * bankroll
    return max(0, min(stake, bankroll * 0.05))  # Cap at 5%


async def find_value_bets(
    home_team: str,
    away_team: str,
    league: str,
    predictions: Dict[str, float]
) -> List[Dict]:
    """
    Find value bets for a match.

    Args:
        home_team: Home team name
        away_team: Away team name
        league: League key
        predictions: Model predictions {'home_win': 0.65, 'draw': 0.20, ...}

    Returns:
        List of value bets with details
    """
    client = OddsAPIClient()

    # Fetch odds for league
    matches = await client.fetch_league_odds(league)

    # Find this specific match
    match_odds = None
    for match in matches:
        if (home_team.lower() in match.get('home_team', '').lower() and
            away_team.lower() in match.get('away_team', '').lower()):
            match_odds = match
            break

    if not match_odds:
        logger.warning(f"No odds found for {home_team} vs {away_team}")
        return []

    # Get best odds for each market
    bookmakers = match_odds.get('bookmakers', [])
    best_h2h = find_best_odds(bookmakers, 'h2h')
    best_totals = find_best_odds(bookmakers, 'totals')

    # Calculate EV for each outcome
    value_bets = []

    # Home win
    if 'home_win' in predictions and 'home_win' in best_h2h:
        ev = calculate_ev(predictions['home_win'], best_h2h['home_win']['odd'])
        if ev > 0.02:  # Minimum 2% EV
            value_bets.append({
                'bet_type': 'home_win',
                'team': home_team,
                'probability': predictions['home_win'],
                'best_odd': best_h2h['home_win']['odd'],
                'bookmaker': best_h2h['home_win']['bookmaker'],
                'ev': ev,
                'ev_percentage': f"{ev*100:.1f}%",
                'ev_score': score_ev_factor(ev),
                'kelly_stake': calculate_kelly_stake(
                    predictions['home_win'],
                    best_h2h['home_win']['odd']
                )
            })

    # Away win
    if 'away_win' in predictions and 'away_win' in best_h2h:
        ev = calculate_ev(predictions['away_win'], best_h2h['away_win']['odd'])
        if ev > 0.02:
            value_bets.append({
                'bet_type': 'away_win',
                'team': away_team,
                'probability': predictions['away_win'],
                'best_odd': best_h2h['away_win']['odd'],
                'bookmaker': best_h2h['away_win']['bookmaker'],
                'ev': ev,
                'ev_percentage': f"{ev*100:.1f}%",
                'ev_score': score_ev_factor(ev),
                'kelly_stake': calculate_kelly_stake(
                    predictions['away_win'],
                    best_h2h['away_win']['odd']
                )
            })

    # Over 2.5
    if 'over_2.5' in predictions and 'over_2.5' in best_totals:
        ev = calculate_ev(predictions['over_2.5'], best_totals['over_2.5']['odd'])
        if ev > 0.02:
            value_bets.append({
                'bet_type': 'over_2.5',
                'team': f"{home_team} vs {away_team}",
                'probability': predictions['over_2.5'],
                'best_odd': best_totals['over_2.5']['odd'],
                'bookmaker': best_totals['over_2.5']['bookmaker'],
                'ev': ev,
                'ev_percentage': f"{ev*100:.1f}%",
                'ev_score': score_ev_factor(ev),
                'kelly_stake': calculate_kelly_stake(
                    predictions['over_2.5'],
                    best_totals['over_2.5']['odd']
                )
            })

    # Sort by EV descending
    value_bets.sort(key=lambda x: x['ev'], reverse=True)

    return value_bets


# Example usage
async def main():
    """Example usage"""

    # Example predictions from model
    predictions = {
        'home_win': 0.65,
        'draw': 0.20,
        'away_win': 0.15,
        'over_2.5': 0.58,
        'under_2.5': 0.42
    }

    # Find value bets
    value_bets = await find_value_bets(
        home_team='Manchester City',
        away_team='Sheffield United',
        league='soccer_epl',
        predictions=predictions
    )

    # Print results
    print("💰 VALUE BETS DETECTED:\n")
    for i, bet in enumerate(value_bets, 1):
        print(f"{i}. {bet['bet_type'].upper()}")
        print(f"   Team: {bet['team']}")
        print(f"   Probability: {bet['probability']*100:.1f}%")
        print(f"   Best odd: {bet['best_odd']} ({bet['bookmaker']})")
        print(f"   EV: {bet['ev_percentage']} ✅")
        print(f"   Score: {bet['ev_score']:.1f}/15")
        print(f"   Kelly stake: ${bet['kelly_stake']:.2f}")
        print()


if __name__ == '__main__':
    asyncio.run(main())
