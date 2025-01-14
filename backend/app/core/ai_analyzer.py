from typing import Dict, Any
import numpy as np
from app.models.betting_code import BettingCode
from app.utils.country_utils import get_country_config

def analyze_betting_code(code: BettingCode) -> Dict[str, Any]:
    """
    Analyze a betting code using AI/ML techniques
    This is a simplified version - in production, you'd want to use more sophisticated ML models
    """
    # Get country-specific configuration
    country_config = get_country_config(code.user_country)
    bookmaker_config = next(
        (b for b in country_config["bookmakers"] if b["id"] == code.bookmaker),
        None
    )
    
    if not bookmaker_config:
        return {
            "summary": "Invalid bookmaker for country",
            "confidenceScore": 0,
            "risk": "high",
            "recommendations": ["Invalid bookmaker configuration"]
        }
    
    # Analyze odds
    odds_score = analyze_odds(code.odds, bookmaker_config)
    
    # Analyze stake
    stake_score = analyze_stake(
        code.stake,
        bookmaker_config["minStake"],
        bookmaker_config["maxStake"]
    )
    
    # Analyze code pattern
    pattern_score = analyze_pattern(code.code, bookmaker_config["pattern"])
    
    # Calculate overall confidence score
    confidence_score = calculate_confidence_score([
        odds_score,
        stake_score,
        pattern_score
    ])
    
    # Generate recommendations
    recommendations = generate_recommendations(
        odds_score,
        stake_score,
        pattern_score,
        bookmaker_config
    )
    
    # Determine risk level
    risk_level = determine_risk_level(confidence_score)
    
    return {
        "summary": generate_summary(confidence_score, risk_level, recommendations),
        "confidenceScore": confidence_score,
        "risk": risk_level,
        "recommendations": recommendations,
        "details": {
            "oddsAnalysis": {
                "score": odds_score,
                "isWithinLimits": bookmaker_config["minOdds"] <= code.odds <= bookmaker_config["maxOdds"]
            },
            "stakeAnalysis": {
                "score": stake_score,
                "isWithinLimits": bookmaker_config["minStake"] <= code.stake <= bookmaker_config["maxStake"]
            },
            "patternAnalysis": {
                "score": pattern_score,
                "matchesFormat": bool(bookmaker_config["pattern"].match(code.code))
            }
        }
    }

def analyze_odds(odds: float, bookmaker_config: Dict) -> float:
    """Analyze the odds value"""
    min_odds = bookmaker_config["minOdds"]
    max_odds = bookmaker_config["maxOdds"]
    
    if odds < min_odds or odds > max_odds:
        return 0.0
    
    # Score based on how reasonable the odds are
    # Higher scores for more reasonable odds ranges
    if odds <= 2.0:
        return 0.9  # Very common odds range
    elif odds <= 5.0:
        return 0.7  # Common odds range
    elif odds <= 10.0:
        return 0.5  # Less common but still reasonable
    else:
        return 0.3  # High odds, potentially risky

def analyze_stake(stake: float, min_stake: float, max_stake: float) -> float:
    """Analyze the stake amount"""
    if stake < min_stake or stake > max_stake:
        return 0.0
    
    # Score based on stake amount relative to limits
    normalized_stake = (stake - min_stake) / (max_stake - min_stake)
    
    if normalized_stake <= 0.2:
        return 0.9  # Conservative stake
    elif normalized_stake <= 0.5:
        return 0.7  # Moderate stake
    elif normalized_stake <= 0.8:
        return 0.5  # Higher stake
    else:
        return 0.3  # Very high stake

def analyze_pattern(code: str, pattern: str) -> float:
    """Analyze if the code matches the expected pattern"""
    try:
        if pattern.match(code):
            return 1.0
        return 0.0
    except:
        return 0.0

def calculate_confidence_score(scores: list) -> float:
    """Calculate overall confidence score"""
    weights = [0.4, 0.3, 0.3]  # Weights for odds, stake, and pattern
    weighted_scores = np.multiply(scores, weights)
    return round(float(np.sum(weighted_scores) * 100), 1)

def determine_risk_level(confidence_score: float) -> str:
    """Determine risk level based on confidence score"""
    if confidence_score >= 80:
        return "low"
    elif confidence_score >= 60:
        return "medium"
    else:
        return "high"

def generate_recommendations(
    odds_score: float,
    stake_score: float,
    pattern_score: float,
    bookmaker_config: Dict
) -> list:
    """Generate recommendations based on analysis"""
    recommendations = []
    
    if odds_score < 0.5:
        recommendations.append(
            f"Odds should be between {bookmaker_config['minOdds']} and {bookmaker_config['maxOdds']}"
        )
    
    if stake_score < 0.5:
        recommendations.append(
            f"Stake should be between {bookmaker_config['minStake']} and {bookmaker_config['maxStake']}"
        )
    
    if pattern_score < 1.0:
        recommendations.append(
            f"Code format should match {bookmaker_config['codeFormat']}"
        )
    
    return recommendations

def generate_summary(confidence_score: float, risk_level: str, recommendations: list) -> str:
    """Generate a human-readable summary"""
    if confidence_score >= 80:
        base_summary = "This code appears to be valid and safe to use."
    elif confidence_score >= 60:
        base_summary = "This code meets basic requirements but has some concerns."
    else:
        base_summary = "This code has significant issues that need to be addressed."
    
    if recommendations:
        base_summary += f" {len(recommendations)} improvement(s) recommended."
    
    return base_summary 