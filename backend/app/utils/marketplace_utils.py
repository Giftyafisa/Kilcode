from fastapi import HTTPException
from typing import Dict, Any

def validate_marketplace_data(data: Dict[str, Any], country_config: Dict[str, Any]) -> None:
    """Validate marketplace data against country-specific requirements"""
    
    # Required fields
    required_fields = [
        'code', 'title', 'description', 'price', 'winProbability', 
        'expectedOdds', 'minStake', 'category', 'bookmaker'
    ]
    for field in required_fields:
        if field not in data or data[field] is None:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    marketplace_settings = country_config.get('marketplace_settings', {})
    
    # Title length validation
    min_title_length = marketplace_settings.get('min_title_length', 10)
    max_title_length = marketplace_settings.get('max_title_length', 100)
    if len(str(data['title'])) < min_title_length:
        raise HTTPException(
            status_code=400,
            detail=f"Title must be at least {min_title_length} characters long"
        )
    if len(str(data['title'])) > max_title_length:
        raise HTTPException(
            status_code=400,
            detail=f"Title cannot exceed {max_title_length} characters"
        )
    
    # Description length validation
    min_desc_length = marketplace_settings.get('min_description_length', 50)
    max_desc_length = marketplace_settings.get('max_description_length', 1000)
    if len(str(data['description'])) < min_desc_length:
        raise HTTPException(
            status_code=400,
            detail=f"Description must be at least {min_desc_length} characters long"
        )
    if len(str(data['description'])) > max_desc_length:
        raise HTTPException(
            status_code=400,
            detail=f"Description cannot exceed {max_desc_length} characters"
        )
    
    # Price validation
    try:
        min_price = marketplace_settings.get('min_price', 0)
        max_price = marketplace_settings.get('max_price', float('inf'))
        price = float(data['price'])
        
        if price < min_price or price > max_price:
            raise HTTPException(
                status_code=400,
                detail=f"Price must be between {country_config['currency']['symbol']}{min_price} and {country_config['currency']['symbol']}{max_price}"
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid price value"
        )
    
    # Win probability validation
    try:
        win_prob = float(data['winProbability'])
        if win_prob < 0 or win_prob > 100:
            raise HTTPException(
                status_code=400,
                detail="Win probability must be between 0 and 100"
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid win probability value"
        )
    
    # Odds validation
    try:
        min_odds = marketplace_settings.get('min_odds', 1.0)
        max_odds = marketplace_settings.get('max_odds', float('inf'))
        odds = float(data['expectedOdds'])
        
        if odds < min_odds or odds > max_odds:
            raise HTTPException(
                status_code=400,
                detail=f"Expected odds must be between {min_odds} and {max_odds}"
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid expected odds value"
        )
    
    # Minimum stake validation
    try:
        min_stake_limit = marketplace_settings.get('min_stake_limit', 0)
        max_stake_limit = marketplace_settings.get('max_stake_limit', float('inf'))
        min_stake = float(data['minStake'])
        
        if min_stake < min_stake_limit or min_stake > max_stake_limit:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum stake must be between {country_config['currency']['symbol']}{min_stake_limit} and {country_config['currency']['symbol']}{max_stake_limit}"
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid minimum stake value"
        )
    
    # Validity period validation
    try:
        validity_hours = int(data.get('validityPeriod', 24))
        max_validity = marketplace_settings.get('max_validity_hours', 72)
        if validity_hours < 1 or validity_hours > max_validity:
            raise HTTPException(
                status_code=400,
                detail=f"Validity period must be between 1 and {max_validity} hours"
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid validity period value"
        )
    
    # Category validation
    valid_categories = marketplace_settings.get('categories', [])
    if not valid_categories:
        raise HTTPException(
            status_code=500,
            detail="No valid categories configured for this country"
        )
    
    category = str(data['category'])
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Bookmaker validation
    bookmaker = str(data['bookmaker']).lower()
    valid_bookmakers = [b['id'].lower() for b in country_config.get('bookmakers', [])]
    if not valid_bookmakers:
        raise HTTPException(
            status_code=500,
            detail="No valid bookmakers configured for this country"
        )
    
    if bookmaker not in valid_bookmakers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid bookmaker. Must be one of: {', '.join(valid_bookmakers)}"
        )
    
    # Tags validation (optional)
    if 'tags' in data:
        max_tags = marketplace_settings.get('max_tags', 10)
        max_tag_length = marketplace_settings.get('max_tag_length', 20)
        
        if len(data['tags']) > max_tags:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {max_tags} tags allowed"
            )
        
        for tag in data['tags']:
            if len(tag) > max_tag_length:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tag length cannot exceed {max_tag_length} characters"
                )

def format_marketplace_code(code: Dict[str, Any], country_config: Dict[str, Any]) -> Dict[str, Any]:
    """Format betting code data for marketplace display"""
    return {
        'id': code['id'],
        'title': code.get('title', 'Betting Code'),
        'description': code['description'],
        'price': code['price'],
        'currency': country_config['currency']['code'],
        'currency_symbol': country_config['currency']['symbol'],
        'win_probability': code['win_probability'],
        'expected_odds': code['expected_odds'],
        'valid_until': code['valid_until'],
        'min_stake': code.get('min_stake'),
        'tags': code.get('tags', []),
        'bookmaker': code['bookmaker'],
        'issuer': code.get('issuer', 'Anonymous'),
        'issuer_type': code.get('issuer_type', 'user'),
        'created_at': code['created_at'],
        'marketplace_status': code['marketplace_status'],
        'country': country_config['name'],
        'category': code.get('category', 'General')
    }