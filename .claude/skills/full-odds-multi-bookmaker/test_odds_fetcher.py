"""
Tests for full-odds-multi-bookmaker skill
"""

import pytest
import asyncio
from odds_fetcher import (
    OddsAPIClient,
    OddsCache,
    find_best_odds,
    calculate_ev,
    score_ev_factor,
    calculate_kelly_stake
)
from datetime import datetime


# Cache tests
def test_cache_set_get():
    """Test cache set and get"""
    cache = OddsCache(ttl_minutes=1)

    data = {'test': 'data'}
    cache.set('key1', data)

    retrieved = cache.get('key1')
    assert retrieved == data


def test_cache_expiry():
    """Test cache expiration"""
    cache = OddsCache(ttl_minutes=0)  # Immediate expiry

    cache.set('key1', {'test': 'data'})

    # Should be None (expired)
    import time
    time.sleep(0.1)
    retrieved = cache.get('key1')
    assert retrieved is None


# Best odds tests
def test_find_best_odds_h2h():
    """Test finding best odds for h2h market"""
    bookmakers_data = [
        {
            'key': 'bet365',
            'markets': [
                {
                    'key': 'h2h',
                    'outcomes': [
                        {'name': 'Home', 'price': 1.85},
                        {'name': 'Draw', 'price': 3.60},
                        {'name': 'Away', 'price': 4.20}
                    ]
                }
            ]
        },
        {
            'key': '1xbet',
            'markets': [
                {
                    'key': 'h2h',
                    'outcomes': [
                        {'name': 'Home', 'price': 1.87},  # Best
                        {'name': 'Draw', 'price': 3.55},
                        {'name': 'Away', 'price': 4.50}  # Best
                    ]
                }
            ]
        },
        {
            'key': 'pinnacle',
            'markets': [
                {
                    'key': 'h2h',
                    'outcomes': [
                        {'name': 'Home', 'price': 1.83},
                        {'name': 'Draw', 'price': 3.75},  # Best
                        {'name': 'Away', 'price': 4.30}
                    ]
                }
            ]
        }
    ]

    best = find_best_odds(bookmakers_data, 'h2h')

    assert best['home_win']['odd'] == 1.87
    assert best['home_win']['bookmaker'] == '1xbet'
    assert best['draw']['odd'] == 3.75
    assert best['draw']['bookmaker'] == 'pinnacle'
    assert best['away_win']['odd'] == 4.50
    assert best['away_win']['bookmaker'] == '1xbet'


# EV calculation tests
def test_calculate_ev_positive():
    """Test EV calculation with positive value"""
    probability = 0.65  # 65%
    odd = 1.87

    ev = calculate_ev(probability, odd)

    # EV = (0.65 × 1.87) - 1 = 0.2155
    assert round(ev, 2) == 0.22  # 22% EV


def test_calculate_ev_negative():
    """Test EV calculation with negative value"""
    probability = 0.45
    odd = 2.00

    ev = calculate_ev(probability, odd)

    # EV = (0.45 × 2.00) - 1 = -0.10
    assert round(ev, 2) == -0.10  # -10% EV


def test_calculate_ev_zero():
    """Test EV calculation at break-even"""
    probability = 0.50
    odd = 2.00

    ev = calculate_ev(probability, odd)

    # EV = (0.50 × 2.00) - 1 = 0.0
    assert ev == 0.0


# Scoring tests
def test_score_ev_factor_excellent():
    """Test scoring with excellent EV"""
    ev = 0.20  # 20% EV
    score = score_ev_factor(ev)
    assert score == 15.0


def test_score_ev_factor_good():
    """Test scoring with good EV"""
    ev = 0.12  # 12% EV
    score = score_ev_factor(ev)
    assert score == 12.0


def test_score_ev_factor_moderate():
    """Test scoring with moderate EV"""
    ev = 0.07  # 7% EV
    score = score_ev_factor(ev)
    assert score == 9.0


def test_score_ev_factor_minimal():
    """Test scoring with minimal EV"""
    ev = 0.03  # 3% EV
    score = score_ev_factor(ev)
    assert score == 6.0


def test_score_ev_factor_none():
    """Test scoring with no value"""
    ev = 0.01  # 1% EV (below threshold)
    score = score_ev_factor(ev)
    assert score == 0.0


# Kelly Criterion tests
def test_kelly_stake_positive_edge():
    """Test Kelly stake with positive edge"""
    probability = 0.60
    odd = 2.00
    bankroll = 1000

    stake = calculate_kelly_stake(probability, odd, bankroll, fraction=0.25)

    # Kelly = (b*p - q) / b = (1*0.6 - 0.4) / 1 = 0.2
    # Fractional Kelly (0.25) = 0.2 * 0.25 = 0.05 = 5%
    # Stake = 1000 * 0.05 = 50
    assert 45 <= stake <= 55  # Allow small variance


def test_kelly_stake_no_edge():
    """Test Kelly stake with no edge"""
    probability = 0.40
    odd = 2.00
    bankroll = 1000

    stake = calculate_kelly_stake(probability, odd, bankroll)

    # Negative Kelly, should return 0
    assert stake == 0.0


def test_kelly_stake_capped():
    """Test Kelly stake is capped at 5%"""
    probability = 0.90  # Huge edge
    odd = 3.00
    bankroll = 1000

    stake = calculate_kelly_stake(probability, odd, bankroll, fraction=1.0)

    # Should be capped at 5% of bankroll = 50
    assert stake == 50.0


# API Client tests (mock)
@pytest.mark.asyncio
async def test_api_client_cache():
    """Test API client uses cache"""
    client = OddsAPIClient(api_key='test_key')

    # Set cache manually
    client.cache.set('soccer_epl:h2h,totals', [{'test': 'data'}])

    # Should hit cache (not make API call)
    result = await client.fetch_league_odds('soccer_epl')

    assert result == [{'test': 'data'}]


# Integration tests
def test_full_workflow():
    """Test complete workflow: fetch -> find best -> calculate EV -> score"""

    # Mock bookmaker data
    bookmakers_data = [
        {
            'key': 'bet365',
            'markets': [
                {
                    'key': 'h2h',
                    'outcomes': [
                        {'name': 'Home', 'price': 1.85},
                        {'name': 'Draw', 'price': 3.60},
                        {'name': 'Away', 'price': 4.20}
                    ]
                }
            ]
        },
        {
            'key': '1xbet',
            'markets': [
                {
                    'key': 'h2h',
                    'outcomes': [
                        {'name': 'Home', 'price': 1.90},  # Best
                        {'name': 'Draw', 'price': 3.50},
                        {'name': 'Away', 'price': 4.00}
                    ]
                }
            ]
        }
    ]

    # Find best odds
    best = find_best_odds(bookmakers_data, 'h2h')

    # Model prediction
    probability = 0.65  # 65% chance home win

    # Calculate EV with best odd
    ev = calculate_ev(probability, best['home_win']['odd'])

    # Score it
    score = score_ev_factor(ev)

    # Assertions
    assert best['home_win']['odd'] == 1.90
    assert best['home_win']['bookmaker'] == '1xbet'
    assert round(ev, 2) == 0.24  # 24% EV
    assert score == 15.0  # Excellent value


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
