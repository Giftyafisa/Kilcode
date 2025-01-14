from pydantic import BaseModel, field_validator, Field, model_validator
from typing import Optional
from datetime import datetime
from app.models.country_config import CountryConfig

class BettingCodeBase(BaseModel):
    bookmaker: str
    code: str
    stake: float = Field(gt=0)
    odds: float = Field(gt=0)
    status: str = "pending"
    user_country: str
    description: Optional[str] = None

    @field_validator('user_country')
    @classmethod
    def validate_country(cls, v: str):
        if not v:
            raise ValueError('User country is required')
        country = v.lower()
        if country not in ['nigeria', 'ghana']:
            raise ValueError('Country must be either Nigeria or Ghana')
        return country

    @field_validator('bookmaker')
    @classmethod
    def validate_bookmaker(cls, v: str, info):
        if not v:
            raise ValueError('Bookmaker is required')
        
        if 'user_country' in info.data:
            country = info.data['user_country'].lower()
            config = CountryConfig.get_config(country)
            bookmaker_config = next(
                (b for b in config['bookmakers'] if b['id'] == v.lower()),
                None
            )
            if not bookmaker_config:
                raise ValueError(f"Invalid bookmaker for {country}")
        
        return v.lower()

    @field_validator('code')
    @classmethod
    def validate_code_format(cls, v: str, info):
        if not v:
            raise ValueError('Betting code is required')
            
        # Clean the code
        code = v.strip().upper()
        
        if 'user_country' in info.data and 'bookmaker' in info.data:
            country = info.data['user_country'].lower()
            bookmaker = info.data['bookmaker'].lower()
            
            # Validate using CountryConfig
            config = CountryConfig.get_config(country)
            bookmaker_config = next(
                (b for b in config['bookmakers'] if b['id'] == bookmaker),
                None
            )
            
            if bookmaker_config and not CountryConfig.validate_betting_code(code, bookmaker, country):
                raise ValueError(f"Invalid code format. Example: {bookmaker_config['codeExample']}")

        return code

    @model_validator(mode='after')
    def validate_amounts(self):
        if not self.user_country:
            raise ValueError('User country is required')
            
        config = CountryConfig.get_config(self.user_country)
        bookmaker_config = next(
            (b for b in config['bookmakers'] if b['id'] == self.bookmaker),
            None
        )
        
        if not bookmaker_config:
            raise ValueError(f"Invalid bookmaker {self.bookmaker} for {self.user_country}")

        # Validate stake
        if self.stake < bookmaker_config['min_stake']:
            raise ValueError(
                f"Minimum stake is {bookmaker_config['currency']} "
                f"{bookmaker_config['min_stake']}"
            )
        if self.stake > bookmaker_config['max_stake']:
            raise ValueError(
                f"Maximum stake is {bookmaker_config['currency']} "
                f"{bookmaker_config['max_stake']}"
            )
        
        # Validate odds
        if self.odds < bookmaker_config['min_odds']:
            raise ValueError(f"Minimum odds is {bookmaker_config['min_odds']}")
        if self.odds > bookmaker_config['max_odds']:
            raise ValueError(f"Maximum odds is {bookmaker_config['max_odds']}")
        
        return self

class BettingCodeCreate(BettingCodeBase):
    class Config:
        json_schema_extra = {
            "example": {
                "bookmaker": "sportybet",
                "code": "SBG-123ABC",
                "stake": 10,
                "odds": 2.0,
                "user_country": "ghana",
                "status": "pending"
            }
        }

class BettingCode(BettingCodeBase):
    id: int
    user_id: int
    potential_winnings: float
    created_at: datetime
    verified_at: Optional[datetime] = None
    verified_by: Optional[int] = None
    admin_note: Optional[str] = None

    class Config:
        from_attributes = True

class BettingCodeUpdate(BaseModel):
    status: str
    admin_note: Optional[str] = None
    rejection_reason: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str):
        if v not in ['won', 'lost', 'pending']:
            raise ValueError('Status must be won, lost, or pending')
        return v