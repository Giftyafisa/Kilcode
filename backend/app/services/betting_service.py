from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime
from decimal import Decimal
import re

from app.models.betting_code import BettingCode
from app.models.user import User
from app.core.notifications import notification_manager
from app.core.logger import logger
from app.core.country_config import CountryConfig

BOOKMAKER_PATTERNS = {
    'nigeria': {
        'nairabet': {
            'pattern': r'^NB-\d{8}$',
            'example': 'NB-33333333'
        }
    }
}

class BettingService:
    @staticmethod
    async def submit_code(
        db: Session,
        user_id: int,
        bookmaker: str,
        code: str,
        odds: float,
        stake: float,
        country: str
    ) -> BettingCode:
        try:
            # Add detailed debug logging
            print("=== Code Submission Debug ===")
            print(f"Received data:")
            print(f"- Bookmaker: {bookmaker}")
            print(f"- Code: {code}")
            print(f"- Country: {country}")
            print(f"- Odds: {odds}")
            print(f"- Stake: {stake}")
            
            if bookmaker.lower() == 'nairabet':
                # Clean and format the code
                code = code.strip().upper()
                if not code.startswith('NB-'):
                    code = f"NB-{code.replace('NB', '')}"
                
                pattern = BOOKMAKER_PATTERNS['nigeria']['nairabet']['pattern']
                print(f"Validating Nairabet code:")
                print(f"- Raw code: {code}")
                print(f"- Pattern: {pattern}")
                print(f"- Matches pattern: {bool(re.match(pattern, code))}")
                
                if not re.match(pattern, code):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid code format for nairabet. Code must be in format: {BOOKMAKER_PATTERNS['nigeria']['nairabet']['example']}"
                    )

            # Validate against country config
            country_config = CountryConfig.get_config(country)
            print(f"Country config: {country_config}")
            
            bookmaker_config = next(
                (b for b in country_config['bookmakers'] if b['id'] == bookmaker),
                None
            )
            print(f"Bookmaker config: {bookmaker_config}")
            
            if not bookmaker_config:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid bookmaker for {country}"
                )

            # Validate odds and stake
            if not (bookmaker_config['min_odds'] <= odds <= bookmaker_config['max_odds']):
                raise HTTPException(
                    status_code=400,
                    detail=f"Odds must be between {bookmaker_config['min_odds']} and {bookmaker_config['max_odds']}"
                )

            if not (bookmaker_config['min_stake'] <= stake <= bookmaker_config['max_stake']):
                raise HTTPException(
                    status_code=400,
                    detail=f"Stake must be between {bookmaker_config['min_stake']} and {bookmaker_config['max_stake']}"
                )

            # Calculate potential winnings with proper decimal handling
            potential_winnings = float(Decimal(str(stake)) * Decimal(str(odds)))

            # Get user for notification
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Create new betting code
            betting_code = BettingCode(
                user_id=user_id,
                bookmaker=bookmaker,
                code=code,
                odds=odds,
                stake=stake,
                potential_winnings=potential_winnings,
                status='pending'
            )

            db.add(betting_code)
            db.commit()
            db.refresh(betting_code)

            # Notify admins of new code
            await notification_manager.notify_betting_code_submission(
                country=country,
                betting_code={
                    "id": betting_code.id,
                    "user_name": user.name,
                    "user_id": user.id,
                    "bookmaker": bookmaker,
                    "code": code,
                    "odds": odds,
                    "stake": stake,
                    "potential_winnings": potential_winnings,
                    "created_at": betting_code.created_at.isoformat()
                }
            )

            return betting_code

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error submitting betting code: {str(e)}")
            await notification_manager.notify_system_error(
                country=country,
                error_type="BETTING_SUBMISSION_ERROR",
                error_message=str(e)
            )
            raise HTTPException(status_code=500, detail="Failed to submit betting code")

    @staticmethod
    async def verify_code(
        db: Session,
        code_id: int,
        admin_id: int,
        status: str,
        note: Optional[str] = None,
        rejection_reason: Optional[str] = None
    ) -> BettingCode:
        try:
            betting_code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
            if not betting_code:
                raise HTTPException(status_code=404, detail="Betting code not found")

            user = db.query(User).filter(User.id == betting_code.user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update code status
            betting_code.status = status
            betting_code.admin_note = note
            betting_code.rejection_reason = rejection_reason
            betting_code.verified_at = datetime.utcnow()

            # If won, update user balance
            winnings = None
            if status == 'won':
                winnings = betting_code.potential_winnings
                user.balance += winnings

            db.commit()
            db.refresh(betting_code)

            # Notify user of verification
            await notification_manager.notify_code_verification(
                user_id=betting_code.user_id,
                code_id=code_id,
                status=status,
                winnings=winnings,
                note=note
            )

            # Notify other admins
            await notification_manager.notify_admin_action(
                country=user.country,
                action_type="CODE_VERIFICATION",
                data={
                    "code_id": code_id,
                    "status": status,
                    "admin_id": admin_id,
                    "user_id": user.id
                }
            )

            return betting_code

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error verifying betting code: {str(e)}")
            await notification_manager.notify_system_error(
                country=user.country if user else "unknown",
                error_type="VERIFICATION_ERROR",
                error_message=str(e)
            )
            raise HTTPException(status_code=500, detail="Failed to verify betting code")

betting_service = BettingService() 