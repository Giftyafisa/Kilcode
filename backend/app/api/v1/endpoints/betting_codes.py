from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, models
from app.models.admin import Admin
from app.schemas.activity import Activity
from app.schemas.betting_code import BettingCode, BettingCodeCreate
from app.api import deps
from app.core.websocket_manager import manager
from datetime import datetime, timedelta
from app.services.activity_service import activity_service
import logging
import re
from app.models.country_config import CountryConfig
from sqlalchemy import func, case

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/submit", response_model=BettingCode)
async def submit_code(
    *,
    db: Session = Depends(deps.get_db),
    code_in: BettingCodeCreate,
    current_user: models.User = Depends(deps.get_current_user)
):
    """Submit a new betting code"""
    try:
        logger.info(f"Received betting code submission from user {current_user.id}")
        
        # Validate user country first
        if not code_in.user_country:
            raise HTTPException(
                status_code=422,
                detail="User country is required"
            )
        
        # Case-insensitive country comparison
        if code_in.user_country.lower() != current_user.country.lower():
            raise HTTPException(
                status_code=400,
                detail=f"User country mismatch. Expected {current_user.country}, got {code_in.user_country}"
            )
            
        # Get country config
        country_config = CountryConfig.get_config(current_user.country)
        
        # Check if user is verified for this country
        if not current_user.is_verified:
            raise HTTPException(
                status_code=403,
                detail=f"User not verified for {current_user.country}. Please complete payment to submit betting codes."
            )
        
        # Validate bookmaker for this country
        valid_bookmaker = next(
            (b for b in country_config['bookmakers'] if b['id'].lower() == code_in.bookmaker.lower()),
            None
        )
        if not valid_bookmaker:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid bookmaker for {current_user.country}"
            )

        # Create betting code
        try:
            betting_code_dict = code_in.model_dump()
            betting_code_dict['potential_winnings'] = code_in.stake * code_in.odds
            betting_code = models.BettingCode(
                **betting_code_dict,
                user_id=current_user.id
            )
            
            db.add(betting_code)
            db.commit()
            db.refresh(betting_code)
            
            # Only notify admins after successful creation
            if betting_code:
                await manager.notify_admin_betting_code(
                    current_user.country.lower(),  # Ensure consistent case
                    {
                        "code_id": betting_code.id,
                        "user_id": current_user.id,
                        "user_name": current_user.name,
                        "bookmaker": betting_code.bookmaker,
                        "code": betting_code.code,
                        "odds": betting_code.odds,
                        "stake": betting_code.stake,
                        "potential_winnings": betting_code.potential_winnings,
                        "created_at": betting_code.created_at.isoformat()
                    }
                )
            
            # Add user_country to the response
            betting_code.user_country = current_user.country
            
            return betting_code
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )
            
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting betting code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/user/activities", response_model=List[Activity])
def get_user_activities(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    activity_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get user's activities with optional filters"""
    return activity_service.get_user_activities(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        activity_type=activity_type,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/user/activity-summary")
def get_user_activity_summary(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    days: int = Query(7, ge=1, le=30)
):
    """Get user's activity summary"""
    return activity_service.get_activity_summary(
        db=db,
        user_id=current_user.id,
        days=days
    )

@router.get("/admin/activities/{country}", response_model=List[Activity])
def get_country_activities(
    *,
    db: Session = Depends(deps.get_db),
    current_user: Admin = Depends(deps.get_current_admin),
    country: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    activity_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get country-specific activities for admin"""
    if current_user.country.lower() != country.lower():
        raise HTTPException(
            status_code=403,
            detail="Admin can only view activities for their assigned country"
        )
    
    return activity_service.get_country_activities(
        db=db,
        country=country,
        skip=skip,
        limit=limit,
        activity_type=activity_type,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/user/codes", response_model=List[BettingCode])
def get_user_codes(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    sort: Optional[str] = "created_at",
    direction: Optional[str] = "desc"
):
    """Get betting codes for the current user"""
    try:
        codes = crud.betting_code.get_by_user(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status,
            sort=sort,
            direction=direction
        )
        
        # Add user_country to each code
        for code in codes:
            code.user_country = current_user.country
            
        return codes
    except Exception as e:
        logger.error(f"Error fetching user betting codes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/admin/pending-codes/{country}", response_model=List[BettingCode])
async def get_pending_codes(
    *,
    db: Session = Depends(deps.get_db),
    current_admin: Admin = Depends(deps.get_current_admin),
    country: str
):
    """Get pending betting codes for admin verification"""
    if current_admin.country.lower() != country.lower():
        raise HTTPException(
            status_code=403,
            detail="Admin can only view codes for their assigned country"
        )
    
    return crud.betting_code.get_pending_by_country(db=db, country=country)

@router.get("/admin/dashboard/statistics")
async def get_dashboard_statistics(
    *,
    db: Session = Depends(deps.get_db),
    current_admin: Admin = Depends(deps.get_current_admin)
):
    """Get dashboard statistics for admin"""
    country = current_admin.country.lower()
    
    # Get total users
    total_users = db.query(func.count(models.User.id)).filter(
        func.lower(models.User.country) == country
    ).scalar()
    
    # Get betting statistics
    betting_stats = db.query(
        func.count(BettingCode.id).label('total_codes'),
        func.count(case([(BettingCode.status == 'pending', 1)])).label('pending_codes'),
        func.count(case([(BettingCode.status == 'won', 1)])).label('won_codes'),
        func.count(case([(BettingCode.status == 'lost', 1)])).label('lost_codes'),
    ).join(models.User).filter(
        func.lower(models.User.country) == country
    ).first()
    
    # Get transaction statistics
    transaction_stats = db.query(
        func.sum(case([(BettingCode.status == 'won', BettingCode.potential_winnings)], else_=0)).label('total_payout'),
        func.count(case([(BettingCode.status == 'pending', 1)])).label('pending_withdrawals')
    ).join(models.User).filter(
        func.lower(models.User.country) == country
    ).first()
    
    return {
        "users": {
            "total": total_users
        },
        "betting": {
            "total_codes": betting_stats.total_codes or 0,
            "pending_codes": betting_stats.pending_codes or 0,
            "won_codes": betting_stats.won_codes or 0,
            "lost_codes": betting_stats.lost_codes or 0
        },
        "transactions": {
            "total_payout": float(transaction_stats.total_payout or 0),
            "pending_withdrawals": transaction_stats.pending_withdrawals or 0
        }
    }

@router.get("/admin/dashboard/pending-verifications")
async def get_pending_verifications(
    *,
    db: Session = Depends(deps.get_db),
    current_admin: Admin = Depends(deps.get_current_admin)
):
    """Get pending betting code verifications for admin"""
    return crud.betting_code.get_pending_by_country(
        db=db,
        country=current_admin.country
    )

@router.get("/admin/dashboard/pending-payments")
async def get_pending_payments(
    *,
    db: Session = Depends(deps.get_db),
    current_admin: Admin = Depends(deps.get_current_admin)
):
    """Get pending registration payments for admin"""
    return crud.payment.get_pending_by_country(
        db=db,
        country=current_admin.country
    )

@router.get("/admin/betting-codes/pending", response_model=List[dict])
async def get_pending_betting_codes(
    *,
    db: Session = Depends(deps.get_db),
    current_admin: Admin = Depends(deps.get_current_admin)
):
    """Get pending betting codes for admin verification"""
    try:
        logger.info(f"Fetching pending codes for admin country: {current_admin.country}")
        pending_codes = crud.betting_code.get_pending_by_country(
            db=db,
            country=current_admin.country
        )
        
        # Format the response to include user details
        formatted_codes = []
        for code in pending_codes:
            user = db.query(models.User).filter(models.User.id == code.user_id).first()
            formatted_codes.append({
                "id": code.id,
                "user_id": code.user_id,
                "user_name": user.name if user else "Unknown",
                "bookmaker": code.bookmaker,
                "code": code.code,
                "stake": float(code.stake),
                "odds": float(code.odds),
                "potential_winnings": float(code.potential_winnings),
                "status": code.status,
                "created_at": code.created_at.isoformat(),
                "country": current_admin.country
            })
        
        logger.info(f"Found {len(formatted_codes)} pending codes")
        return formatted_codes
    except Exception as e:
        logger.error(f"Error fetching pending codes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching pending codes: {str(e)}"
        )

@router.post("/admin/betting-codes/{code_id}/verify")
async def verify_betting_code(
    *,
    db: Session = Depends(deps.get_db),
    current_admin: Admin = Depends(deps.get_current_admin),
    code_id: int,
    status: str
):
    """Verify a betting code"""
    try:
        logger.info(f"Verifying code {code_id} as {status} by admin {current_admin.email}")
        
        # Get the betting code
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Betting code not found")
            
        # Get the user's country
        user = db.query(models.User).filter(models.User.id == code.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Verify admin has permission for this country
        if user.country.lower() != current_admin.country.lower():
            raise HTTPException(
                status_code=403,
                detail="Admin can only verify codes from their assigned country"
            )
            
        # Update the code status
        code.status = status
        code.verified_at = datetime.utcnow()
        code.verified_by = current_admin.id
        
        db.commit()
        
        # Notify the user via WebSocket
        await manager.notify_user(user.email, {
            "type": "CODE_VERIFIED",
            "data": {
                "code_id": code.id,
                "status": status,
                "verified_at": code.verified_at.isoformat()
            }
        })
        
        return {"message": "Code verified successfully"}
        
    except Exception as e:
        logger.error(f"Error verifying betting code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying betting code: {str(e)}"
        )
  