from typing import Dict, Any
import re

# Country-specific configurations
COUNTRY_CONFIGS = {
    "nigeria": {
        "name": "Nigeria",
        "currency": {
            "code": "NGN",
            "symbol": "₦",
            "name": "Nigerian Naira"
        },
        "bookmakers": [
            {
                "id": "bet9ja",
                "name": "Bet9ja",
                "codeFormat": "B9J-XXXXXX",
                "pattern": re.compile(r"^(?:B9J-)?[A-Z0-9]{6,12}$", re.I),
                "minStake": 100,
                "maxStake": 500000,
                "minOdds": 1.2,
                "maxOdds": 1000
            },
            {
                "id": "sportybet",
                "name": "SportyBet",
                "codeFormat": "SB-XXXXXX",
                "pattern": re.compile(r"^(?:SB-)?[A-Z0-9]{6,12}$", re.I),
                "minStake": 100,
                "maxStake": 500000,
                "minOdds": 1.2,
                "maxOdds": 1000
            }
        ],
        "analysis_requirements": {
            "min_confidence_score": 70,
            "required_fields": ["analysis", "confidence_score", "risk_assessment"],
            "min_analysis_length": 50
        },
        "marketplace_settings": {
            "min_price": 100,  # Minimum price in NGN
            "max_price": 50000,  # Maximum price in NGN
            "min_odds": 1.2,  # Minimum odds for marketplace codes
            "max_odds": 1000,  # Maximum odds for marketplace codes
            "min_stake_limit": 100,  # Minimum stake limit in NGN
            "max_stake_limit": 500000,  # Maximum stake limit in NGN
            "max_validity_hours": 72,  # Maximum validity period in hours
            "min_description_length": 50,  # Minimum description length
            "max_description_length": 1000,  # Maximum description length
            "min_title_length": 10,  # Minimum title length
            "max_title_length": 100,  # Maximum title length
            "max_tags": 10,  # Maximum number of tags
            "max_tag_length": 20,  # Maximum length of each tag
            "categories": [
                "Football",
                "Basketball",
                "Tennis",
                "Multiple Sports",
                "Premium",
                "General"
            ]
        }
    },
    "ghana": {
        "name": "Ghana",
        "currency": {
            "code": "GHS",
            "symbol": "GH₵",
            "name": "Ghana Cedi"
        },
        "bookmakers": [
            {
                "id": "sportybet",
                "name": "SportyBet Ghana",
                "codeFormat": "SBG-XXXXXX",
                "pattern": re.compile(r"^(?:SBG-)?[A-Z0-9]{6,12}$", re.I),
                "minStake": 1,
                "maxStake": 10000,
                "minOdds": 1.2,
                "maxOdds": 1000
            },
            {
                "id": "betway",
                "name": "Betway Ghana",
                "codeFormat": "BW-XXXXXX",
                "pattern": re.compile(r"^(?:BW-)?[A-Z0-9]{6,12}$", re.I),
                "minStake": 1,
                "maxStake": 5000,
                "minOdds": 1.2,
                "maxOdds": 1000
            }
        ],
        "analysis_requirements": {
            "min_confidence_score": 75,
            "required_fields": ["analysis", "confidence_score", "risk_assessment"],
            "min_analysis_length": 50
        },
        "marketplace_settings": {
            "min_price": 1,  # Minimum price in GHS
            "max_price": 1000,  # Maximum price in GHS
            "min_odds": 1.2,  # Minimum odds for marketplace codes
            "max_odds": 1000,  # Maximum odds for marketplace codes
            "min_stake_limit": 1,  # Minimum stake limit in GHS
            "max_stake_limit": 10000,  # Maximum stake limit in GHS
            "max_validity_hours": 72,  # Maximum validity period in hours
            "min_description_length": 50,  # Minimum description length
            "max_description_length": 1000,  # Maximum description length
            "min_title_length": 10,  # Minimum title length
            "max_title_length": 100,  # Maximum title length
            "max_tags": 10,  # Maximum number of tags
            "max_tag_length": 20,  # Maximum length of each tag
            "categories": [
                "Football",
                "Basketball",
                "Tennis",
                "Multiple Sports",
                "Premium",
                "General"
            ]
        }
    }
}

def get_country_config(country: str) -> Dict[str, Any]:
    """Get configuration for a specific country"""
    country = country.lower()
    if country not in COUNTRY_CONFIGS:
        raise ValueError(f"Configuration not found for country: {country}")
    return COUNTRY_CONFIGS[country]

def validate_country_specific_code(code: Any, country_config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a betting code against country-specific rules"""
    try:
        errors = []
        
        # Validate title length
        if len(code.get('title', '')) < country_config['marketplace_settings']['min_title_length']:
            errors.append(f"Title must be at least {country_config['marketplace_settings']['min_title_length']} characters long")
        if len(code.get('title', '')) > country_config['marketplace_settings']['max_title_length']:
            errors.append(f"Title cannot exceed {country_config['marketplace_settings']['max_title_length']} characters")
        
        # Validate description length
        if len(code.get('description', '')) < country_config['marketplace_settings']['min_description_length']:
            errors.append(f"Description must be at least {country_config['marketplace_settings']['min_description_length']} characters long")
        if len(code.get('description', '')) > country_config['marketplace_settings']['max_description_length']:
            errors.append(f"Description cannot exceed {country_config['marketplace_settings']['max_description_length']} characters")
        
        # Validate price
        price = float(code.get('price', 0))
        if price < country_config['marketplace_settings']['min_price']:
            errors.append(f"Price must be at least {country_config['currency']['symbol']}{country_config['marketplace_settings']['min_price']}")
        if price > country_config['marketplace_settings']['max_price']:
            errors.append(f"Price cannot exceed {country_config['currency']['symbol']}{country_config['marketplace_settings']['max_price']}")
        
        # Validate odds
        odds = float(code.get('expectedOdds', 0))
        if odds < country_config['marketplace_settings']['min_odds']:
            errors.append(f"Expected odds must be at least {country_config['marketplace_settings']['min_odds']}")
        if odds > country_config['marketplace_settings']['max_odds']:
            errors.append(f"Expected odds cannot exceed {country_config['marketplace_settings']['max_odds']}")
        
        # Validate stake limits
        min_stake = float(code.get('minStake', 0))
        if min_stake < country_config['marketplace_settings']['min_stake_limit']:
            errors.append(f"Minimum stake must be at least {country_config['currency']['symbol']}{country_config['marketplace_settings']['min_stake_limit']}")
        if min_stake > country_config['marketplace_settings']['max_stake_limit']:
            errors.append(f"Minimum stake cannot exceed {country_config['currency']['symbol']}{country_config['marketplace_settings']['max_stake_limit']}")
        
        # Validate win probability
        win_prob = float(code.get('winProbability', 0))
        if win_prob < 0 or win_prob > 100:
            errors.append("Win probability must be between 0 and 100")
        
        # Validate validity period
        validity_hours = int(code.get('validityPeriod', 24))
        if validity_hours < 1:
            errors.append("Validity period must be at least 1 hour")
        if validity_hours > country_config['marketplace_settings']['max_validity_hours']:
            errors.append(f"Validity period cannot exceed {country_config['marketplace_settings']['max_validity_hours']} hours")
        
        # Validate category
        if code.get('category') not in country_config['marketplace_settings']['categories']:
            errors.append("Invalid category")
        
        # Validate tags if present
        tags = code.get('tags', [])
        if len(tags) > country_config['marketplace_settings']['max_tags']:
            errors.append(f"Maximum {country_config['marketplace_settings']['max_tags']} tags allowed")
        for tag in tags:
            if len(tag) > country_config['marketplace_settings']['max_tag_length']:
                errors.append(f"Tag length cannot exceed {country_config['marketplace_settings']['max_tag_length']} characters")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
        
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [str(e)]
        }

def format_currency(amount: float, country: str) -> str:
    """Format currency amount according to country"""
    country_config = get_country_config(country)
    currency = country_config["currency"]
    return f"{currency['symbol']}{amount:,.2f}"

def get_bookmaker_config(country: str, bookmaker_id: str) -> Dict[str, Any]:
    """Get configuration for a specific bookmaker in a country"""
    country_config = get_country_config(country)
    bookmaker = next(
        (b for b in country_config["bookmakers"] if b["id"] == bookmaker_id),
        None
    )
    if not bookmaker:
        raise ValueError(f"Bookmaker {bookmaker_id} not found for country {country}")
    return bookmaker

def get_marketplace_settings(country: str) -> Dict[str, Any]:
    """Get marketplace settings for a specific country"""
    country_config = get_country_config(country)
    return country_config.get("marketplace_settings", {})