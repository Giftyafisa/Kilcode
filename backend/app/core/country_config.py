from typing import Dict, List
from decimal import Decimal
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
                    'code_format': 'B9J-XXXXXX to B9J-XXXXXXXXXXXX',
                    'codeExample': 'B9J-A12B34 or B9J-123456789012',
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
                    'code_format': 'SB-XXXXXX to SB-XXXXXXXXXXXX',
                    'codeExample': 'SB-A12B34 or SB-123456789012',
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
                    'code_format': 'NB-XXXXXX to NB-XXXXXXXXXXXX',
                    'codeExample': 'NB-A12B34 or NB-123456789012',
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
                    'code_format': 'MB-XXXXXX to MB-XXXXXXXXXXXX',
                    'codeExample': 'MB-A12B34 or MB-123456789012',
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
                    'code_format': 'BB-XXXXXX to BB-XXXXXXXXXXXX',
                    'codeExample': 'BB-A12B34 or BB-123456789012',
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
                    'name': '1xBet Nigeria',
                    'code_format': '1X-XXXXXX to 1X-XXXXXXXXXXXX',
                    'codeExample': '1X-A12B34 or 1X-123456789012',
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
                    'code_format': 'SBG-XXXXXX to SBG-XXXXXXXXXXXX',
                    'codeExample': 'SBG-A12B34 or SBG-123456789012',
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
                    'code_format': 'BW-XXXXXX to BW-XXXXXXXXXXXX',
                    'codeExample': 'BW-A12B34 or BW-123456789012',
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
                    'code_format': 'SC-XXXXXX to SC-XXXXXXXXXXXX',
                    'codeExample': 'SC-A12B34 or SC-123456789012',
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
                    'code_format': 'BB-XXXXXX to BB-XXXXXXXXXXXX',
                    'codeExample': 'BB-A12B34 or BB-123456789012',
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
                    'code_format': '1X-XXXXXX to 1X-XXXXXXXXXXXX',
                    'codeExample': '1X-A12B34 or 1X-123456789012',
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
                    'code_format': 'PB-XXXXXX to PB-XXXXXXXXXXXX',
                    'codeExample': 'PB-A12B34 or PB-123456789012',
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
        return cls.CONFIGS.get(country.lower(), cls.CONFIGS['ghana']) 