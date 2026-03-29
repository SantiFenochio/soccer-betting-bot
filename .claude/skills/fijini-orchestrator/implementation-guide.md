# 🔧 Fijini Orchestrator - Implementation Guide

Este documento proporciona ejemplos de código para implementar el orquestador.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FIJINI ORCHESTRATOR                       │
│                      (Lead Agent)                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─► [Phase 1] Data Fetcher (Serial)
             │   │
             │   └─► Returns: 20-50 matches
             │
             ├─► [Phase 2] Parallel Analysis
             │   │
             │   ├─► xG Analyzer ────────┐
             │   ├─► Value Detector ─────┤─► Run in Parallel
             │   └─► Context Analyzer ───┘
             │       │
             │       └─► Returns: Score matrices
             │
             ├─► [Phase 3] Scoring & Ranking (Lead Agent)
             │   │
             │   └─► Aggregate + Sort + TOP 3
             │
             └─► [Phase 4] Report Generator
                 │
                 └─► Telegram formatted output
```

---

## 📝 Code Examples

### 1. Main Orchestrator Function

```python
# fijini_orchestrator.py

from datetime import datetime
from typing import List, Dict
import asyncio

class FijiniOrchestrator:
    """
    Lead agent for /fijini command.
    Orchestrates parallel subagents to find TOP 3 daily locks.
    """

    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.min_score_threshold = 75  # 3 stars minimum

    async def execute(self) -> str:
        """
        Main execution flow for /fijini command.
        Returns: Formatted Telegram message with TOP 3 locks
        """
        try:
            # Phase 1: Fetch all matches
            matches = await self.fetch_matches()

            if not matches:
                return "❌ No se encontraron partidos para hoy."

            # Phase 2: Parallel analysis (3 subagents)
            analysis_results = await self.parallel_analysis(matches)

            # Phase 3: Score and rank
            scored_bets = self.score_and_rank(matches, analysis_results)

            # Filter by threshold
            top_locks = [
                bet for bet in scored_bets
                if bet['total_score'] >= self.min_score_threshold
            ][:3]  # Top 3

            if not top_locks:
                return self.no_locks_message()

            # Phase 4: Format output
            return self.format_telegram_output(top_locks)

        except Exception as e:
            return f"❌ Error al analizar mercado: {str(e)}"

    async def fetch_matches(self) -> List[Dict]:
        """Phase 1: Data Fetcher"""
        # Use football-data skill or API
        matches = await get_matches_for_date(self.today)
        return matches

    async def parallel_analysis(self, matches: List[Dict]) -> Dict:
        """Phase 2: Run 3 analyzers in parallel"""
        tasks = [
            self.analyze_xg(matches),
            self.detect_value(matches),
            self.analyze_context(matches)
        ]

        results = await asyncio.gather(*tasks)

        return {
            'xg': results[0],
            'value': results[1],
            'context': results[2]
        }

    def score_and_rank(self, matches: List[Dict],
                       analysis: Dict) -> List[Dict]:
        """Phase 3: Aggregate scores and rank"""
        scored_bets = []

        for match in matches:
            # Get all predictions for this match
            predictions = self.get_predictions_for_match(match)

            for pred in predictions:
                score_breakdown = {
                    'base': self.score_base_confidence(pred),
                    'form': analysis['context'][match['id']]['form'],
                    'xg': analysis['xg'][match['id']][pred['type']],
                    'h2h': analysis['context'][match['id']]['h2h'],
                    'value': analysis['value'][match['id']][pred['type']]
                }

                total = sum(score_breakdown.values())

                # Consistency bonus
                high_scores = sum(
                    1 for s in score_breakdown.values() if s >= 15
                )
                if high_scores >= 3:
                    total += 10

                total = min(total, 100)  # Cap at 100

                scored_bets.append({
                    'match': match,
                    'prediction': pred,
                    'score_breakdown': score_breakdown,
                    'total_score': total,
                    'stars': self.assign_stars(total)
                })

        # Sort by score descending
        return sorted(scored_bets,
                     key=lambda x: x['total_score'],
                     reverse=True)

    def assign_stars(self, score: float) -> str:
        """Convert score to star rating"""
        if score >= 90:
            return "⭐⭐⭐⭐⭐"
        elif score >= 80:
            return "⭐⭐⭐⭐"
        elif score >= 75:
            return "⭐⭐⭐"
        elif score >= 70:
            return "⭐⭐"
        else:
            return "⭐"

    def format_telegram_output(self, top_locks: List[Dict]) -> str:
        """Phase 4: Format for Telegram"""
        medals = ["🥇", "🥈", "🥉"]
        output = []

        output.append("🔥 **FIJINI - TOP 3 LOCKS DEL DÍA** 🔥\n")
        output.append("Las 3 mejores apuestas con mayor probabilidad de éxito")
        output.append("Análisis multi-factorial: xG + Form + H2H + Value\n")
        output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        for idx, lock in enumerate(top_locks):
            match = lock['match']
            pred = lock['prediction']
            scores = lock['score_breakdown']

            output.append(f"{medals[idx]} **LOCK #{idx+1}** {lock['stars']}")
            output.append("━━━━━━━━━━━━━━━━━\n")
            output.append(f"⚽ **Partido:** {match['home']} vs {match['away']}")
            output.append(f"🏆 **Liga:** {match['league']}")
            output.append(f"🕐 **Hora:** {match['time']}\n")
            output.append("🎯 **APUESTA RECOMENDADA:**")
            output.append(f"   💡 {pred['bet_description']}")
            output.append(f"   📊 Confianza: {pred['confidence']}%")
            output.append(f"   🎲 Score Total: {lock['total_score']:.1f}/100\n")
            output.append("📈 **Análisis Multi-Factorial:**")
            output.append(f"   • Base: {scores['base']:.0f}/30")
            output.append(f"   • Forma: {scores['form']:.0f}/20")
            output.append(f"   • xG: {scores['xg']:.0f}/20")
            output.append(f"   • H2H: {scores['h2h']:.0f}/15")
            output.append(f"   • Value: {scores['value']:.0f}/15\n")
            output.append("🔍 **Factores Clave:**")

            # Add key factors
            key_factors = self.get_key_factors(lock)
            for factor in key_factors:
                output.append(f"   ✓ {factor}")

            output.append(f"\n💭 {pred['reasoning']}\n")
            output.append("━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # Add methodology
        output.append("\n📊 **METODOLOGÍA:**")
        output.append("Análisis basado en 5 factores:")
        output.append("• Confianza base del modelo")
        output.append("• Forma/momentum reciente")
        output.append("• Expected Goals (xG)")
        output.append("• Historial head-to-head")
        output.append("• Expected Value (EV)\n")

        output.append("⭐ **RATING:**")
        output.append("⭐⭐⭐⭐⭐ = Lock máximo (90+)")
        output.append("⭐⭐⭐⭐ = Muy confiable (80+)")
        output.append("⭐⭐⭐ = Confiable (75+)\n")

        output.append("💡 **RECOMENDACIÓN:**")
        output.append("• Locks con 4-5⭐ → Apuesta con confianza")
        output.append("• Locks con 3⭐ → Apuesta moderada")
        output.append("• Usar Kelly Criterion para stakes\n")

        output.append("⚠️ Ninguna predicción es 100% segura.")
        output.append("⚠️ Apuesta responsablemente.")

        return "\n".join(output)

    def no_locks_message(self) -> str:
        """Message when no quality locks found"""
        return (
            "⚠️ **No se encontraron locks de alta calidad hoy.**\n\n"
            "El análisis multi-factorial no identificó apuestas que cumplan "
            "con los criterios de calidad (75+ puntos).\n\n"
            "💡 **Recuerda:** No apostar es mejor que apostar mal.\n"
            "Espera a mejores oportunidades mañana. 🎯"
        )
```

---

### 2. Subagent: xG Analyzer

```python
# subagents/xg_analyzer.py

class XGAnalyzer:
    """
    Subagent 2: Analyze Expected Goals for all matches.
    Returns scores 0-20 per match/bet type.
    """

    async def analyze(self, matches: List[Dict]) -> Dict:
        """
        Analyze xG for all matches.
        Returns: {match_id: {bet_type: score}}
        """
        results = {}

        for match in matches:
            home_xg = await self.get_team_xg(match['home'])
            away_xg = await self.get_team_xg(match['away'])

            results[match['id']] = {
                'over_2_5': self.score_over_under(
                    home_xg + away_xg, 2.5, 'over'
                ),
                'under_2_5': self.score_over_under(
                    home_xg + away_xg, 2.5, 'under'
                ),
                'home_win': self.score_result(home_xg, away_xg, 'home'),
                'away_win': self.score_result(home_xg, away_xg, 'away'),
                'btts': self.score_btts(home_xg, away_xg)
            }

        return results

    def score_over_under(self, total_xg: float,
                         line: float, direction: str) -> float:
        """Score Over/Under based on xG"""
        if direction == 'over':
            if total_xg >= line + 1.0:
                return 20.0
            elif total_xg >= line + 0.5:
                return 16.0
            elif total_xg >= line:
                return 12.0
            else:
                return 8.0
        else:  # under
            if total_xg <= line - 1.0:
                return 20.0
            elif total_xg <= line - 0.5:
                return 16.0
            elif total_xg <= line:
                return 12.0
            else:
                return 8.0

    def score_result(self, home_xg: float, away_xg: float,
                     result: str) -> float:
        """Score match result based on xG differential"""
        diff = home_xg - away_xg

        if result == 'home':
            if diff >= 1.5:
                return 20.0
            elif diff >= 1.0:
                return 16.0
            elif diff >= 0.5:
                return 12.0
            else:
                return 8.0
        else:  # away
            if diff <= -1.5:
                return 20.0
            elif diff <= -1.0:
                return 16.0
            elif diff <= -0.5:
                return 12.0
            else:
                return 8.0
```

---

### 3. Subagent: Value Detector

```python
# subagents/value_detector.py

class ValueDetector:
    """
    Subagent 3: Calculate Expected Value for all bets.
    Returns scores 0-15 per match/bet type.
    """

    async def analyze(self, matches: List[Dict]) -> Dict:
        """
        Calculate EV for all bets.
        Returns: {match_id: {bet_type: score}}
        """
        results = {}

        for match in matches:
            odds = await self.get_odds(match)
            probabilities = await self.get_probabilities(match)

            results[match['id']] = {}

            for bet_type, odd in odds.items():
                prob = probabilities.get(bet_type, 0)
                ev = (prob * odd) - 1  # Expected Value formula

                results[match['id']][bet_type] = self.score_ev(ev)

        return results

    def score_ev(self, ev: float) -> float:
        """Score based on Expected Value percentage"""
        if ev >= 0.15:  # 15%+ EV
            return 15.0
        elif ev >= 0.10:  # 10%+ EV
            return 12.0
        elif ev >= 0.05:  # 5%+ EV
            return 9.0
        elif ev >= 0.02:  # 2%+ EV
            return 6.0
        else:
            return 0.0

    def calculate_kelly_stake(self, probability: float,
                             odds: float,
                             bankroll: float,
                             fraction: float = 0.25) -> float:
        """
        Calculate Kelly Criterion stake.
        Using fractional Kelly (25%) for safety.
        """
        b = odds - 1  # Decimal odds to 'b'
        p = probability
        q = 1 - p

        kelly = (b * p - q) / b
        kelly_stake = kelly * fraction * bankroll

        return max(0, kelly_stake)  # Never negative
```

---

### 4. Subagent: Context Analyzer

```python
# subagents/context_analyzer.py

class ContextAnalyzer:
    """
    Subagent 4: Analyze Form, H2H, Momentum, Injuries.
    Returns scores for form (0-20) and h2h (0-15).
    """

    async def analyze(self, matches: List[Dict]) -> Dict:
        """
        Analyze context for all matches.
        Returns: {match_id: {'form': score, 'h2h': score}}
        """
        results = {}

        for match in matches:
            home_form = await self.get_team_form(match['home'])
            away_form = await self.get_team_form(match['away'])
            h2h = await self.get_h2h(match['home'], match['away'])
            injuries = await self.get_injuries(match['home'], match['away'])

            results[match['id']] = {
                'form': self.score_form(home_form, away_form),
                'h2h': self.score_h2h(h2h),
                'injuries': injuries  # For key factors
            }

        return results

    def score_form(self, home_form: Dict, away_form: Dict) -> float:
        """Score based on recent form (last 5 matches)"""
        home_ppg = home_form['points'] / 5
        away_ppg = away_form['points'] / 5

        # For home win
        if home_ppg >= 2.5 and away_ppg <= 1.0:
            return 20.0
        elif home_ppg >= 2.0 and away_ppg <= 1.5:
            return 17.0
        elif home_ppg >= 1.5:
            return 14.0
        elif home_ppg >= 1.0:
            return 10.0
        else:
            return 5.0

    def score_h2h(self, h2h: List[Dict]) -> float:
        """Score based on H2H pattern strength"""
        if not h2h or len(h2h) < 3:
            return 7.0  # Neutral if insufficient data

        # Analyze pattern (e.g., Over 2.5 in last 5 H2H)
        pattern_strength = self.detect_pattern(h2h)

        if pattern_strength >= 0.8:  # 4/5 or 5/5
            return 15.0
        elif pattern_strength >= 0.6:  # 3/5
            return 11.0
        elif pattern_strength >= 0.4:  # 2/5
            return 7.0
        else:
            return 3.0
```

---

### 5. Integration with Bot

```python
# bot.py - Add /fijini handler

from fijini_orchestrator import FijiniOrchestrator

async def fijini_command(update: Update, context: ContextContext):
    """
    Handler for /fijini command.
    Uses FijiniOrchestrator to get TOP 3 daily locks.
    """
    chat_id = update.effective_chat.id

    # Send "analyzing" message
    await context.bot.send_message(
        chat_id=chat_id,
        text="🔍 Analizando todo el mercado del día...\n"
             "Esto puede tomar 30-60 segundos. ⏳"
    )

    # Execute orchestrator
    orchestrator = FijiniOrchestrator()
    result = await orchestrator.execute()

    # Send result
    await context.bot.send_message(
        chat_id=chat_id,
        text=result,
        parse_mode='Markdown'
    )

# Register handler
application.add_handler(CommandHandler('fijini', fijini_command))
```

---

## 🧪 Testing Examples

```python
# tests/test_fijini_orchestrator.py

import pytest
from fijini_orchestrator import FijiniOrchestrator

@pytest.mark.asyncio
async def test_fijini_with_good_locks():
    """Test when there are quality locks available"""
    orchestrator = FijiniOrchestrator()
    result = await orchestrator.execute()

    assert "🔥 FIJINI - TOP 3 LOCKS DEL DÍA 🔥" in result
    assert "🥇 LOCK #1" in result
    assert "⭐" in result  # Has star ratings

@pytest.mark.asyncio
async def test_fijini_no_matches():
    """Test when no matches are available"""
    orchestrator = FijiniOrchestrator()
    # Mock to return empty matches
    result = await orchestrator.execute()

    assert "No se encontraron partidos" in result

@pytest.mark.asyncio
async def test_fijini_low_quality_day():
    """Test when no locks meet threshold"""
    orchestrator = FijiniOrchestrator()
    # Mock to return low scores
    result = await orchestrator.execute()

    assert "No se encontraron locks de alta calidad" in result
```

---

## 📊 Performance Monitoring

```python
# monitoring/fijini_tracker.py

class FijiniPerformanceTracker:
    """Track /fijini command performance over time"""

    def track_execution(self, locks: List[Dict]):
        """Record locks for later validation"""
        for lock in locks:
            self.db.insert({
                'date': datetime.now(),
                'match': lock['match']['id'],
                'bet_type': lock['prediction']['type'],
                'total_score': lock['total_score'],
                'stars': lock['stars'],
                'result': None  # To be filled later
            })

    def calculate_win_rate_by_stars(self) -> Dict:
        """Calculate historical win rate per star rating"""
        results = self.db.query("""
            SELECT stars, AVG(CASE WHEN result = 'won' THEN 1 ELSE 0 END)
            FROM locks
            WHERE result IS NOT NULL
            GROUP BY stars
        """)

        return results

    def validate_target_precision(self) -> bool:
        """Check if meeting 67-75% target"""
        overall_wr = self.db.query("""
            SELECT AVG(CASE WHEN result = 'won' THEN 1 ELSE 0 END)
            FROM locks
            WHERE result IS NOT NULL
        """)

        return 0.67 <= overall_wr <= 0.75
```

---

## 🚀 Deployment Checklist

- [ ] All 5 subagents implemented
- [ ] Parallel execution tested
- [ ] Error handling verified
- [ ] Telegram formatting validated
- [ ] Star rating logic correct
- [ ] Consistency bonus applied correctly
- [ ] Quality threshold (75 pts) enforced
- [ ] No locks message works
- [ ] Performance tracking enabled
- [ ] Win rate monitoring active

---

**Ready to orchestrate! 🎯**
