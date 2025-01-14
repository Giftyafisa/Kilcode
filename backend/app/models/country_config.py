from typing import Dict
from pydantic import BaseModel
import re

class CountryConfig:
    CONFIGS: Dict[str, Dict] = {
        'nigeria': {
            'currency': {
                'code': 'NGN',
                'symbol': '₦',
                'name': 'Nigerian Naira'
            },
            'bookmakers': [
                {
                    'id': 'bet9ja',
                    'name': 'Bet9ja',
                    'code_format': 'B9J-XXXXXX',
                    'codeExample': 'B9J-123ABC',
                    'prefix': 'B9J-',
                    'pattern': r'^(?:B9J-)?[A-Z0-9]{6,12}$',
                    'min_stake': 100,
                    'max_stake': 500000,
                    'currency': 'NGN',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'sportybet',
                    'name': 'SportyBet',
                    'code_format': 'SB-XXXXXX',
                    'codeExample': 'SB-123ABC',
                    'prefix': 'SB-',
                    'pattern': r'^(?:SB-)?[A-Z0-9]{6,12}$',
                    'min_stake': 100,
                    'max_stake': 500000,
                    'currency': 'NGN',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'nairabet',
                    'name': 'NairaBet',
                    'code_format': 'NB-XXXXXX',
                    'codeExample': 'NB-123ABC',
                    'prefix': 'NB-',
                    'pattern': r'^(?:NB-)?[A-Z0-9]{6,12}$',
                    'min_stake': 100,
                    'max_stake': 500000,
                    'currency': 'NGN',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'merrybet',
                    'name': 'MerryBet',
                    'code_format': 'MB-XXXXXX',
                    'codeExample': 'MB-123ABC',
                    'prefix': 'MB-',
                    'pattern': r'^(?:MB-)?[A-Z0-9]{6,12}$',
                    'min_stake': 100,
                    'max_stake': 500000,
                    'currency': 'NGN',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'bangbet',
                    'name': 'BangBet',
                    'code_format': 'BB-XXXXXX',
                    'codeExample': 'BB-123ABC',
                    'prefix': 'BB-',
                    'pattern': r'^(?:BB-)?[A-Z0-9]{6,12}$',
                    'min_stake': 100,
                    'max_stake': 500000,
                    'currency': 'NGN',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': '1xbet',
                    'name': '1xBet',
                    'code_format': '1X-XXXXXX',
                    'codeExample': '1X-123ABC',
                    'prefix': '1X-',
                    'pattern': r'^(?:1X-)?[A-Z0-9]{6,12}$',
                    'min_stake': 100,
                    'max_stake': 1000000,
                    'currency': 'NGN',
                    'min_odds': 1.2,
                    'max_odds': 1000
                }
            ]
        },
        'ghana': {
            'currency': {
                'code': 'GHS',
                'symbol': 'GH₵',
                'name': 'Ghana Cedis'
            },
            'bookmakers': [
                {
                    'id': 'sportybet',
                    'name': 'SportyBet Ghana',
                    'code_format': 'SBG-XXXXXX',
                    'codeExample': 'SBG-123ABC',
                    'prefix': 'SBG-',
                    'pattern': r'^(?:SBG-)?[A-Z0-9]{6,12}$',
                    'min_stake': 1,
                    'max_stake': 10000,
                    'currency': 'GHS',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'betway',
                    'name': 'Betway Ghana',
                    'code_format': 'BW-XXXXXX',
                    'codeExample': 'BW-123ABC',
                    'prefix': 'BW-',
                    'pattern': r'^(?:BW-)?[A-Z0-9]{6,12}$',
                    'min_stake': 1,
                    'max_stake': 5000,
                    'currency': 'GHS',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'soccarbet',
                    'name': 'SoccarBet Ghana',
                    'code_format': 'SC-XXXXXX',
                    'codeExample': 'SC-123ABC',
                    'prefix': 'SC-',
                    'pattern': r'^(?:SC-)?[A-Z0-9]{6,12}$',
                    'min_stake': 1,
                    'max_stake': 5000,
                    'currency': 'GHS',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'bangbet',
                    'name': 'BangBet Ghana',
                    'code_format': 'BB-XXXXXX',
                    'codeExample': 'BB-123ABC',
                    'prefix': 'BB-',
                    'pattern': r'^(?:BB-)?[A-Z0-9]{6,12}$',
                    'min_stake': 1,
                    'max_stake': 5000,
                    'currency': 'GHS',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': '1xbet',
                    'name': '1xBet Ghana',
                    'code_format': '1X-XXXXXX',
                    'codeExample': '1X-123ABC',
                    'prefix': '1X-',
                    'pattern': r'^(?:1X-)?[A-Z0-9]{6,12}$',
                    'min_stake': 1,
                    'max_stake': 10000,
                    'currency': 'GHS',
                    'min_odds': 1.2,
                    'max_odds': 1000
                },
                {
                    'id': 'premierbet',
                    'name': 'PremierBet Ghana',
                    'code_format': 'PB-XXXXXX',
                    'codeExample': 'PB-123ABC',
                    'prefix': 'PB-',
                    'pattern': r'^(?:PB-)?[A-Z0-9]{6,12}$',
                    'min_stake': 1,
                    'max_stake': 5000,
                    'currency': 'GHS',
                    'min_odds': 1.2,
                    'max_odds': 1000
                }
            ]
        }
    }

    @classmethod
    def get_config(cls, country: str) -> Dict:
        """Get configuration for a specific country"""
        return cls.CONFIGS.get(country.lower(), cls.CONFIGS['ghana'])

    @classmethod
    def validate_betting_code(cls, code: str, bookmaker: str, country: str) -> bool:
        """Validate betting code format for a specific bookmaker and country"""
        config = cls.get_config(country)
        bookmaker_config = next(
            (b for b in config['bookmakers'] if b['id'] == bookmaker),
            None
        )
        if not bookmaker_config:
            return False
            
        # Clean the code
        code = code.strip().upper()
        
        # Add prefix if missing
        prefix = bookmaker_config['prefix']
        if not code.startswith(prefix):
            code = f"{prefix}{code}"
            
        # Use the country-specific pattern
        pattern = bookmaker_config['pattern']
        return bool(re.match(pattern, code)) 