"""
Integration with value_bets.py and fijini-orchestrator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .odds_fetcher import (
    OddsAPIClient,
    find_best_odds,
    calculate_ev,
    score_ev_factor,
    find_value_bets
)
import asyncio
from typing import Dict, List


async def enhance_value_bets_analysis(
    match_data: Dict,
    predictions: Dict
) -> Dict:
    """
    Enhance value_bets.py with real odds from API.

    Args:
        match_data: {
            'home': 'Manchester City',
            'away': 'Sheffield United',
            'league': 'soccer_epl'
        }
        predictions: {
            'home_win_prob': 0.65,
            'draw_prob': 0.20,
            'away_win_prob': 0.15,
            'over_2_5_prob': 0.58
        }

    Returns:
        Enhanced analysis with real odds
    """
    # Convert predictions to format expected by find_value_bets
    formatted_predictions = {
        'home_win': predictions.get('home_win_prob', 0),
        'draw': predictions.get('draw_prob', 0),
        'away_win': predictions.get('away_win_prob', 0),
        'over_2.5': predictions.get('over_2_5_prob', 0),
        'under_2.5': 1 - predictions.get('over_2_5_prob', 0)
    }

    # Find value bets
    value_bets = await find_value_bets(
        home_team=match_data['home'],
        away_team=match_data['away'],
        league=match_data.get('league', 'soccer_epl'),
        predictions=formatted_predictions
    )

    # Return enhanced analysis
    return {
        'match': f"{match_data['home']} vs {match_data['away']}",
        'league': match_data.get('league'),
        'value_bets': value_bets,
        'best_value': value_bets[0] if value_bets else None,
        'total_value_bets': len(value_bets)
    }


async def get_value_score_for_orchestrator(
    match_data: Dict,
    predictions: Dict
) -> float:
    """
    Get value score (0-15) for fijini-orchestrator Factor 5.

    Args:
        match_data: Match information
        predictions: Model predictions

    Returns:
        Score from 0-15 points
    """
    analysis = await enhance_value_bets_analysis(match_data, predictions)

    if analysis['best_value']:
        return analysis['best_value']['ev_score']
    else:
        return 0.0


async def batch_analyze_matches(matches: List[Dict]) -> List[Dict]:
    """
    Analyze multiple matches for value bets.

    Args:
        matches: List of match data with predictions

    Returns:
        List of enhanced analyses
    """
    tasks = [
        enhance_value_bets_analysis(match['data'], match['predictions'])
        for match in matches
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [
        result for result in results
        if not isinstance(result, Exception)
    ]


# Example integration with value_bets.py
def integrate_with_value_bets():
    """
    Example of how to integrate with existing value_bets.py
    """
    code_example = '''
# In value_bets.py, modify calculate_value() function:

from skills.full_odds_multi_bookmaker.integration import (
    enhance_value_bets_analysis
)
import asyncio

async def calculate_value_enhanced(home_team, away_team, predictions):
    """Enhanced version using real odds"""

    match_data = {
        'home': home_team,
        'away': away_team,
        'league': 'soccer_epl'  # Or detect from team
    }

    # Get real odds and calculate EV
    analysis = await enhance_value_bets_analysis(match_data, predictions)

    return analysis

# Usage:
result = asyncio.run(calculate_value_enhanced(
    'Manchester City',
    'Sheffield United',
    {'home_win_prob': 0.65, 'over_2_5_prob': 0.58}
))
    '''
    return code_example


# Example integration with fijini-orchestrator
def integrate_with_orchestrator():
    """
    Example of how fijini-orchestrator uses this skill
    """
    code_example = '''
# In fijini-orchestrator, Subagent 3: Value Detector

from skills.full_odds_multi_bookmaker.integration import (
    get_value_score_for_orchestrator
)

async def value_detector_subagent(matches):
    """Subagent 3: Detect value bets using real odds"""

    results = {}

    for match in matches:
        # Get value score (0-15 points)
        value_score = await get_value_score_for_orchestrator(
            match_data={
                'home': match['home_team'],
                'away': match['away_team'],
                'league': match['league']
            },
            predictions=match['predictions']
        )

        results[match['id']] = {
            'value_score': value_score
        }

    return results
    '''
    return code_example


if __name__ == '__main__':
    # Print integration examples
    print("=== INTEGRATION WITH value_bets.py ===\n")
    print(integrate_with_value_bets())
    print("\n=== INTEGRATION WITH fijini-orchestrator ===\n")
    print(integrate_with_orchestrator())
