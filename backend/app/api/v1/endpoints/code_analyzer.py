from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.db.session import get_db
from app.core.auth import get_current_admin
from app.models.admin import Admin
from app.models.betting_code import BettingCode
from app.models.code_analysis import CodeAnalysis, AnalysisStatus, RiskLevel
from app.models.analysis_comment import AnalysisComment
from app.utils.country_utils import get_country_config, validate_country_specific_code
from datetime import datetime, timedelta
from app.utils.marketplace_utils import validate_marketplace_data
import logging
from sqlalchemy import func
from app.models.code_view import CodeView
from app.models.code_purchase import CodePurchase
from app.models.code_rating import CodeRating
from sqlalchemy import or_
from sqlalchemy import case, and_

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/countries")
async def get_available_countries():
    """Get list of available countries with their configurations"""
    try:
        from app.utils.country_utils import COUNTRY_CONFIGS
        
        countries = []
        for country_code, config in COUNTRY_CONFIGS.items():
            countries.append({
                "code": country_code.upper(),
                "name": config["name"],
                "currency": config["currency"],
                "bookmakers": [
                    {
                        "id": bm["id"],
                        "name": bm["name"]
                    } for bm in config["bookmakers"]
                ],
                "marketplace_settings": config["marketplace_settings"]
            })
        
        return countries
    except Exception as e:
        logger.error(f"Error fetching available countries: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching available countries")

@router.get("/pending-analysis")
async def get_pending_analyses(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get betting codes pending analysis for admin's country"""
    try:
        country = current_admin.country.lower()
        country_config = get_country_config(country)
        
        # Get allowed bookmakers for this country
        allowed_bookmakers = [b["id"] for b in country_config["bookmakers"]]
        
        codes = db.query(BettingCode).filter(
            BettingCode.analysis_status == "pending",
            BettingCode.user_country == country,
            BettingCode.bookmaker.in_(allowed_bookmakers)
        ).all()
        
        return [code.to_dict() for code in codes]
    except Exception as e:
        logger.error(f"Error fetching pending analyses: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching pending analyses")

@router.post("/analyze/{code_id}")
async def create_analysis(
    code_id: int,
    risk_level: RiskLevel,
    expert_analysis: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new analysis for a betting code with country-specific validation"""
    try:
        # Get betting code
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Betting code not found")
            
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot analyze codes from other countries")
        
        # Get country-specific requirements
        country_config = get_country_config(country)
        requirements = country_config["analysis_requirements"]
        
        # Validate analysis length
        if len(expert_analysis) < requirements["min_analysis_length"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Analysis must be at least {requirements['min_analysis_length']} characters long"
            )
            
        # Create analysis
        analysis = CodeAnalysis(
            betting_code_id=code_id,
            analyst_id=current_admin.id,
            status=AnalysisStatus.IN_PROGRESS,
            risk_level=risk_level,
            expert_analysis=expert_analysis,
            country=country,
            bookmaker=code.bookmaker
        )
        
        db.add(analysis)
        
        # Update betting code
        code.current_analysis_id = analysis.id
        code.analysis_status = "in_progress"
        
        db.commit()
        return analysis.to_dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating analysis")

@router.post("/comment/{analysis_id}")
async def add_comment(
    analysis_id: int,
    comment: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Add a comment to an analysis with country-specific validation"""
    try:
        # Get analysis
        analysis = db.query(CodeAnalysis).filter(CodeAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        # Verify country access
        country = current_admin.country.lower()
        if analysis.country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot comment on analyses from other countries")
            
        # Create comment
        comment = AnalysisComment(
            analysis_id=analysis_id,
            admin_id=current_admin.id,
            comment=comment
        )
        
        db.add(comment)
        db.commit()
        return comment.to_dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error adding comment")

@router.put("/complete/{analysis_id}")
async def complete_analysis(
    analysis_id: int,
    confidence_score: float,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Complete an analysis with country-specific validation"""
    try:
        # Get analysis
        analysis = db.query(CodeAnalysis).filter(CodeAnalysis.id == analysis_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
            
        # Verify ownership
        if analysis.analyst_id != current_admin.id:
            raise HTTPException(status_code=403, detail="Can only complete your own analyses")
            
        # Get country-specific requirements
        country = current_admin.country.lower()
        country_config = get_country_config(country)
        min_confidence = country_config["analysis_requirements"]["min_confidence_score"]
        
        # Validate confidence score
        if confidence_score < min_confidence:
            raise HTTPException(
                status_code=400,
                detail=f"Confidence score must be at least {min_confidence} for {country}"
            )
            
        # Update analysis
        analysis.status = AnalysisStatus.COMPLETED
        analysis.confidence_score = confidence_score
        
        # Update betting code
        code = analysis.betting_code
        code.analysis_status = "completed"
        
        db.commit()
        return analysis.to_dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error completing analysis: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error completing analysis")

@router.get("/requirements")
async def get_country_requirements(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get country-specific analysis requirements"""
    try:
        country = current_admin.country.lower()
        country_config = get_country_config(country)
        return {
            "country": country,
            "requirements": country_config["analysis_requirements"],
            "bookmakers": country_config["bookmakers"]
        }
    except Exception as e:
        logger.error(f"Error fetching country requirements: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching country requirements")

@router.post("/marketplace/{code_id}")
async def publish_to_marketplace(
    code_id: int,
    marketplace_data: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Publish an analyzed code to the marketplace with country-specific validation"""
    try:
        # Get betting code
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Betting code not found")
            
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot publish codes from other countries")
            
        # Verify code is analyzed and completed
        if code.analysis_status != "completed":
            raise HTTPException(status_code=400, detail="Only completed analyses can be published")
            
        # Get country-specific requirements
        country_config = get_country_config(country)
        
        # Validate marketplace data
        validate_marketplace_data(marketplace_data, country_config)
        
        # Calculate validity period
        valid_until = datetime.utcnow() + timedelta(hours=int(marketplace_data.get('validityPeriod', 24)))
        
        # Update code with marketplace data
        code.price = marketplace_data.get('price')
        code.description = marketplace_data.get('description')
        code.tags = marketplace_data.get('tags', [])
        code.win_probability = marketplace_data.get('winProbability')
        code.expected_odds = marketplace_data.get('expectedOdds')
        code.valid_until = valid_until
        code.min_stake = marketplace_data.get('minStake')
        code.is_published = marketplace_data.get('isPublished', False)
        code.marketplace_status = 'active' if marketplace_data.get('isPublished') else 'draft'
        
        db.commit()
        return code.to_dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error publishing to marketplace: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error publishing to marketplace")

@router.get("/marketplace-codes")
async def get_marketplace_codes(
    db: Session = Depends(get_db),
    country: Optional[str] = None,
    page: int = 1,
    limit: int = 12,
    min_win_prob: Optional[float] = None,
    min_odds: Optional[float] = None,
    max_odds: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    issuer: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc",
    filter: Optional[str] = None,
    search: Optional[str] = None
):
    """Get marketplace codes with advanced filtering"""
    try:
        if not country:
            raise HTTPException(status_code=400, detail="Country is required")
            
        country = country.lower()
        if country not in ['nigeria', 'ghana']:
            raise HTTPException(status_code=400, detail="Invalid country")

        # Base query with required filters
        query = db.query(BettingCode).filter(
            BettingCode.user_country == country,
            BettingCode.is_published == True,
            BettingCode.marketplace_status == 'active',
            BettingCode.status == 'approved'
        )

        # Add valid_until check only if it exists
        query = query.filter(
            or_(
                BettingCode.valid_until == None,
                BettingCode.valid_until > datetime.utcnow()
            )
        )
        
        # Apply optional filters
        if min_win_prob:
            query = query.filter(BettingCode.win_probability >= min_win_prob)
        if min_odds:
            query = query.filter(BettingCode.expected_odds >= min_odds)
        if max_odds:
            query = query.filter(BettingCode.expected_odds <= max_odds)
        if min_price:
            query = query.filter(BettingCode.price >= min_price)
        if max_price:
            query = query.filter(BettingCode.price <= max_price)
        if issuer:
            query = query.filter(BettingCode.issuer.ilike(f"%{issuer}%"))
        if start_date:
            query = query.filter(BettingCode.created_at >= start_date)
        if end_date:
            query = query.filter(BettingCode.created_at <= end_date)
        if search:
            search_filter = or_(
                BettingCode.title.ilike(f"%{search}%"),
                BettingCode.description.ilike(f"%{search}%"),
                BettingCode.bookmaker.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
            
        # Get total count before pagination
        total = query.count()
        
        logger.info(f"Found {total} codes for country {country}")
            
        # Apply sorting
        if sort_by:
            sort_column = getattr(BettingCode, sort_by, BettingCode.created_at)
            if sort_direction == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
            # Default sort by created_at desc
            query = query.order_by(BettingCode.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Get paginated results
        codes = query.all()
        
        # Log the results
        logger.info(f"Returning {len(codes)} codes for page {page}")
        
        # Return formatted response
        return {
            "items": [code.to_dict() for code in codes],
            "total": total,
            "page": page,
            "limit": limit,
            "success": True
        }
    except HTTPException as e:
        logger.error(f"HTTP Exception in get_marketplace_codes: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching marketplace codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching marketplace codes")

@router.put("/marketplace-status/{code_id}")
async def update_marketplace_status(
    code_id: int,
    status: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update marketplace status of a code"""
    try:
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Code not found")
            
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot update codes from other countries")
            
        valid_statuses = ['active', 'draft', 'expired', 'sold']
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
            
        code.marketplace_status = status
        if status == 'expired':
            code.is_published = False
            
        db.commit()
        return code.to_dict()
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error updating marketplace status: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error updating marketplace status")

@router.get("/country-config/{country}")
async def get_country_config_endpoint(
    country: str,
    current_admin: Admin = Depends(get_current_admin)
):
    """Get country-specific configuration"""
    try:
        # Verify admin has access to this country
        admin_country = current_admin.country.lower()
        requested_country = country.lower()
        
        if admin_country != requested_country:
            raise HTTPException(
                status_code=403,
                detail="Cannot access configuration for other countries"
            )
            
        config = get_country_config(requested_country)
        return {
            "country": requested_country,
            "config": config
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching country config: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching country configuration")

@router.get("/submitted-codes")
async def get_submitted_codes(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    min_odds: Optional[float] = None,
    max_odds: Optional[float] = None,
    bookmaker: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_direction: str = "desc"
):
    """Get all submitted codes that need analysis"""
    try:
        country = current_admin.country.lower()
        country_config = get_country_config(country)
        
        # Get allowed bookmakers for this country
        allowed_bookmakers = [b["id"] for b in country_config["bookmakers"]]
        
        # Get all submitted codes that haven't been analyzed yet
        query = db.query(BettingCode).join(BettingCode.user).filter(
            BettingCode.user.has(country=country),  # User's country matches admin's country
            BettingCode.bookmaker.in_(allowed_bookmakers),
            BettingCode.status == 'pending',  # Only pending codes
            BettingCode.analysis_status == 'pending'  # Not yet analyzed
        )
        
        # Apply filters
        if bookmaker:
            query = query.filter(BettingCode.bookmaker == bookmaker)
            
        if min_odds is not None:
            query = query.filter(BettingCode.odds >= min_odds)
            
        if max_odds is not None:
            query = query.filter(BettingCode.odds <= max_odds)
            
        if start_date:
            query = query.filter(BettingCode.created_at >= start_date)
            
        if end_date:
            query = query.filter(BettingCode.created_at <= end_date)
        
        # Apply sorting
        if sort_by and hasattr(BettingCode, sort_by):
            sort_column = getattr(BettingCode, sort_by)
            if sort_direction.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
        else:
            # Default sort by created_at desc
            query = query.order_by(BettingCode.created_at.desc())
        
        codes = query.all()
        
        # Return detailed code information
        return [{
            **code.to_dict(),
            'description': code.description or 'No description available',
            'bookmaker_name': next(
                (b['name'] for b in country_config['bookmakers'] if b['id'] == code.bookmaker),
                code.bookmaker
            ),
            'user_name': code.user.name if code.user else 'Unknown',
            'country_name': country_config.get('name', country.upper()),
            'currency': country_config['currency']['code'],
            'currency_symbol': country_config['currency']['symbol']
        } for code in codes]
        
    except Exception as e:
        logger.error(f"Error fetching submitted codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching submitted codes")

@router.get("/marketplace/stats")
async def get_marketplace_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get marketplace statistics for the admin's country"""
    try:
        country = current_admin.country.lower()
        
        # Get total active listings
        active_listings = db.query(BettingCode).filter(
            BettingCode.marketplace_status == 'active',
            BettingCode.valid_until > datetime.utcnow(),
            BettingCode.user_country == country
        ).count()
        
        # Get total revenue
        total_revenue = db.query(func.sum(CodePurchase.amount)).join(
            BettingCode, CodePurchase.code_id == BettingCode.id
        ).filter(
            BettingCode.user_country == country
        ).scalar() or 0
        
        # Get average win rate
        won_codes = db.query(BettingCode).filter(
            BettingCode.status == 'won',
            BettingCode.user_country == country
        ).count()
        
        total_sold = db.query(BettingCode).filter(
            BettingCode.marketplace_status == 'sold',
            BettingCode.user_country == country
        ).count()
        
        avg_win_rate = (won_codes / total_sold * 100) if total_sold > 0 else 0
        
        # Get total analyzed codes for the country
        total_analyzed = db.query(CodeAnalysis).join(
            BettingCode, CodeAnalysis.betting_code_id == BettingCode.id
        ).filter(
            BettingCode.user_country == country
        ).count()
        
        # Get total published codes for the country
        total_published = db.query(BettingCode).filter(
            BettingCode.marketplace_status == 'active',
            BettingCode.user_country == country
        ).count()
        
        return {
            "active_listings": active_listings,
            "total_revenue": float(total_revenue),
            "avg_win_rate": round(avg_win_rate, 2),
            "total_analyzed": total_analyzed,
            "total_published": total_published
        }
    except Exception as e:
        logger.error(f"Error fetching marketplace stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching marketplace statistics")

@router.get("/marketplace/analytics")
async def get_marketplace_analytics(
    timeframe: str = "7d",
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed marketplace analytics for the specified timeframe"""
    try:
        country = current_admin.country.lower()
        
        # Calculate start date based on timeframe
        now = datetime.utcnow()
        if timeframe == "24h":
            start_date = now - timedelta(days=1)
        elif timeframe == "7d":
            start_date = now - timedelta(days=7)
        elif timeframe == "30d":
            start_date = now - timedelta(days=30)
        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe")
            
        # Get analytics data
        analytics = {
            "sales": db.query(BettingCode).filter(
                BettingCode.user_country == country,
                BettingCode.marketplace_status == 'sold',
                BettingCode.updated_at >= start_date
            ).count(),
            
            "revenue": float(db.query(func.sum(BettingCode.price)).filter(
                BettingCode.user_country == country,
                BettingCode.marketplace_status == 'sold',
                BettingCode.updated_at >= start_date
            ).scalar() or 0),
            
            "new_listings": db.query(BettingCode).filter(
                BettingCode.user_country == country,
                BettingCode.is_published == True,
                BettingCode.created_at >= start_date
            ).count(),
            
            "avg_price": float(db.query(func.avg(BettingCode.price)).filter(
                BettingCode.user_country == country,
                BettingCode.is_published == True,
                BettingCode.created_at >= start_date
            ).scalar() or 0)
        }
        
        return analytics
    except Exception as e:
        logger.error(f"Error fetching marketplace analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching marketplace analytics")

@router.post("/validate")
async def validate_code(
    code_data: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Validate a code before publishing to marketplace"""
    try:
        country = current_admin.country.lower()
        country_config = get_country_config(country)
        
        validation_result = validate_country_specific_code(code_data, country_config)
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Code validation failed",
                    "errors": validation_result["errors"]
                }
            )
        
        return {"message": "Code validation successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error validating code: {str(e)}")
        raise HTTPException(status_code=500, detail="Error validating code")

@router.get("/marketplace/categories")
async def get_marketplace_categories(
    current_admin: Admin = Depends(get_current_admin)
):
    """Get marketplace categories for the admin's country"""
    try:
        country = current_admin.country.lower()
        country_config = get_country_config(country)
        
        return {
            "categories": country_config.get("marketplace_categories", []),
            "country": country
        }
    except Exception as e:
        logger.error(f"Error fetching marketplace categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching marketplace categories")

@router.get("/codes/{code_id}/analytics")
async def get_code_analytics(
    code_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific code"""
    try:
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Code not found")
            
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot access codes from other countries")
            
        # Get code analytics
        analytics = {
            "views": db.query(func.count(CodeView.id)).filter(
                CodeView.code_id == code_id
            ).scalar(),
            
            "purchases": db.query(func.count(CodePurchase.id)).filter(
                CodePurchase.code_id == code_id
            ).scalar(),
            
            "revenue": float(db.query(func.sum(CodePurchase.amount)).filter(
                CodePurchase.code_id == code_id
            ).scalar() or 0),
            
            "average_rating": float(db.query(func.avg(CodeRating.rating)).filter(
                CodeRating.code_id == code_id
            ).scalar() or 0),
            
            "total_ratings": db.query(CodeRating).filter(
                CodeRating.code_id == code_id
            ).count()
        }
        
        return analytics
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching code analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching code analytics")

@router.get("/marketplace/trending")
async def get_trending_codes(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    timeframe: str = "7d"
):
    """Get trending codes based on views, purchases, and ratings"""
    try:
        country = current_admin.country.lower()
        
        # Calculate start date based on timeframe
        now = datetime.utcnow()
        if timeframe == "24h":
            start_date = now - timedelta(days=1)
        elif timeframe == "7d":
            start_date = now - timedelta(days=7)
        elif timeframe == "30d":
            start_date = now - timedelta(days=30)
        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe")
        
        # Get codes with their stats
        trending_codes = (
            db.query(
                BettingCode,
                func.count(CodeView.id).label('view_count'),
                func.count(CodePurchase.id).label('purchase_count'),
                func.avg(CodeRating.rating).label('avg_rating')
            )
            .outerjoin(CodeView, CodeView.code_id == BettingCode.id)
            .outerjoin(CodePurchase, CodePurchase.code_id == BettingCode.id)
            .outerjoin(CodeRating, CodeRating.code_id == BettingCode.id)
            .filter(
                BettingCode.user_country == country,
                BettingCode.is_published == True,
                BettingCode.marketplace_status == 'active',
                BettingCode.valid_until > datetime.utcnow(),
                or_(
                    CodeView.viewed_at >= start_date,
                    CodePurchase.purchased_at >= start_date,
                    CodeRating.created_at >= start_date
                )
            )
            .group_by(BettingCode.id)
            .order_by(
                (func.count(CodeView.id) * 0.3 +
                 func.count(CodePurchase.id) * 0.5 +
                 func.coalesce(func.avg(CodeRating.rating), 0) * 0.2).desc()
            )
            .limit(10)
            .all()
        )
        
        return [{
            **code.to_dict(),
            'stats': {
                'views': view_count,
                'purchases': purchase_count,
                'rating': float(avg_rating) if avg_rating else 0
            }
        } for code, view_count, purchase_count, avg_rating in trending_codes]
        
    except Exception as e:
        logger.error(f"Error fetching trending codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching trending codes")

@router.get("/marketplace/search")
async def search_marketplace_codes(
    query: str,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    min_rating: Optional[float] = None,
    min_win_rate: Optional[float] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None
):
    """Search marketplace codes with advanced filtering"""
    try:
        country = current_admin.country.lower()
        
        # Base query
        base_query = (
            db.query(
                BettingCode,
                func.avg(CodeRating.rating).label('avg_rating'),
                func.count(CodePurchase.id).label('purchase_count')
            )
            .outerjoin(CodeRating, CodeRating.code_id == BettingCode.id)
            .outerjoin(CodePurchase, CodePurchase.code_id == BettingCode.id)
            .filter(
                BettingCode.user_country == country,
                BettingCode.is_published == True,
                BettingCode.marketplace_status == 'active',
                BettingCode.valid_until > datetime.utcnow()
            )
        )
        
        # Apply text search
        if query:
            search_filter = or_(
                BettingCode.title.ilike(f"%{query}%"),
                BettingCode.description.ilike(f"%{query}%"),
                BettingCode.tags.contains([query])
            )
            base_query = base_query.filter(search_filter)
        
        # Apply filters
        if min_rating:
            base_query = base_query.having(func.avg(CodeRating.rating) >= min_rating)
        
        if min_win_rate:
            base_query = base_query.filter(BettingCode.win_probability >= min_win_rate)
        
        if category:
            base_query = base_query.filter(BettingCode.category == category)
        
        # Group by
        base_query = base_query.group_by(BettingCode.id)
        
        # Apply sorting
        if sort_by == "rating":
            base_query = base_query.order_by(func.avg(CodeRating.rating).desc())
        elif sort_by == "popularity":
            base_query = base_query.order_by(func.count(CodePurchase.id).desc())
        elif sort_by == "price":
            base_query = base_query.order_by(BettingCode.price.asc())
        elif sort_by == "win_probability":
            base_query = base_query.order_by(BettingCode.win_probability.desc())
        else:
            base_query = base_query.order_by(BettingCode.created_at.desc())
        
        results = base_query.all()
        
        return [{
            **code.to_dict(),
            'stats': {
                'rating': float(avg_rating) if avg_rating else 0,
                'purchases': purchase_count
            }
        } for code, avg_rating, purchase_count in results]
        
    except Exception as e:
        logger.error(f"Error searching marketplace codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching marketplace codes")

@router.post("/codes/{code_id}/rate")
async def rate_code(
    code_id: int,
    rating: float,
    comment: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Rate a code and provide optional feedback"""
    try:
        # Validate rating
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Get code
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Code not found")
        
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot rate codes from other countries")
        
        # Check if admin has already rated this code
        existing_rating = db.query(CodeRating).filter(
            CodeRating.code_id == code_id,
            CodeRating.rater_id == current_admin.id
        ).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating
            existing_rating.comment = comment
            existing_rating.updated_at = datetime.utcnow()
        else:
            # Create new rating
            new_rating = CodeRating(
                code_id=code_id,
                rater_id=current_admin.id,
                rating=rating,
                comment=comment
            )
            db.add(new_rating)
        
        db.commit()
        return {"message": "Rating submitted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error rating code: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error submitting rating")

@router.get("/codes/{code_id}/ratings")
async def get_code_ratings(
    code_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """Get ratings and reviews for a specific code"""
    try:
        # Get code
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Code not found")
        
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot access ratings from other countries")
        
        # Get ratings with admin info
        ratings = (
            db.query(CodeRating, Admin)
            .join(Admin, CodeRating.rater_id == Admin.id)
            .filter(CodeRating.code_id == code_id)
            .order_by(CodeRating.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [{
            **rating.to_dict(),
            'rater': {
                'id': admin.id,
                'name': admin.full_name,
                'role': admin.role
            }
        } for rating, admin in ratings]
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching code ratings: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching code ratings")

@router.get("/marketplace/recommendations")
async def get_code_recommendations(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    min_success_rate: float = 0.7,
    max_price: Optional[float] = None
):
    """Get personalized code recommendations based on performance and criteria"""
    try:
        country = current_admin.country.lower()
        
        # Base query for active marketplace codes
        base_query = (
            db.query(
                BettingCode,
                func.avg(CodeRating.rating).label('avg_rating'),
                func.count(CodePurchase.id).label('purchase_count'),
                func.sum(case((CodeAnalysis.status == 'won', 1), else_=0)).label('wins'),
                func.count(CodeAnalysis.id).label('total_analyzed')
            )
            .outerjoin(CodeRating, CodeRating.code_id == BettingCode.id)
            .outerjoin(CodePurchase, CodePurchase.code_id == BettingCode.id)
            .outerjoin(CodeAnalysis, CodeAnalysis.betting_code_id == BettingCode.id)
            .filter(
                BettingCode.user_country == country,
                BettingCode.is_published == True,
                BettingCode.marketplace_status == 'active',
                BettingCode.valid_until > datetime.utcnow()
            )
        )
        
        # Apply category filter if specified and not null
        if category and category.lower() != 'null':
            base_query = base_query.filter(BettingCode.category == category)
        
        # Apply price filter if specified and valid
        if max_price and max_price != float('inf') and str(max_price).lower() != 'undefined':
            try:
                max_price_float = float(max_price)
                base_query = base_query.filter(BettingCode.price <= max_price_float)
            except (ValueError, TypeError):
                pass  # Skip invalid price values
        
        # Group and calculate success rate
        recommendations = (
            base_query.group_by(BettingCode.id)
            .having(
                and_(
                    func.count(CodeAnalysis.id) > 0,  # Must have analyses
                    func.sum(case((CodeAnalysis.status == 'won', 1), else_=0)) / func.count(CodeAnalysis.id) >= min_success_rate
                )
            )
            .order_by(
                (func.sum(case((CodeAnalysis.status == 'won', 1), else_=0)) / func.count(CodeAnalysis.id)).desc(),
                func.avg(CodeRating.rating).desc()
            )
            .limit(10)
            .all()
        )
        
        return [{
            **code.to_dict(),
            'stats': {
                'rating': float(avg_rating) if avg_rating else 0,
                'purchases': purchase_count,
                'success_rate': (wins / total_analyzed * 100) if total_analyzed > 0 else 0
            }
        } for code, avg_rating, purchase_count, wins, total_analyzed in recommendations]
        
    except Exception as e:
        logger.error(f"Error fetching code recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching code recommendations")

@router.get("/marketplace/performance")
async def get_marketplace_performance(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    timeframe: str = "30d"
):
    """Get detailed marketplace performance metrics"""
    try:
        country = current_admin.country.lower()
        
        # Calculate start date based on timeframe
        now = datetime.utcnow()
        if timeframe == "7d":
            start_date = now - timedelta(days=7)
        elif timeframe == "30d":
            start_date = now - timedelta(days=30)
        elif timeframe == "90d":
            start_date = now - timedelta(days=90)
        else:
            raise HTTPException(status_code=400, detail="Invalid timeframe")
        
        # Get performance metrics
        performance = {
            "revenue": {
                "total": 0,
                "by_category": {}
            },
            "success_rates": {
                "overall": 0,
                "by_category": {}
            },
            "popular_categories": [],
            "price_performance": {
                "optimal_range": None,
                "by_range": []
            }
        }
        
        try:
            # Get total revenue
            total_revenue = db.query(func.sum(CodePurchase.amount)).scalar() or 0
            performance["revenue"]["total"] = float(total_revenue)
        except Exception as e:
            logger.error(f"Error getting total revenue: {str(e)}")
        
        try:
            # Get revenue by category
            category_revenue = (
                db.query(
                    BettingCode.category,
                    func.sum(CodePurchase.amount).label('revenue')
                )
                .join(CodePurchase, CodePurchase.code_id == BettingCode.id)
                .group_by(BettingCode.category)
                .all()
            )
            
            performance["revenue"]["by_category"] = {
                cat: float(rev) for cat, rev in category_revenue if cat is not None
            }
        except Exception as e:
            logger.error(f"Error getting category revenue: {str(e)}")
        
        try:
            # Calculate success rates
            success_rates = (
                db.query(
                    BettingCode.category,
                    func.count(BettingCode.id).label('total'),
                    func.sum(case((BettingCode.status == 'won', 1), else_=0)).label('wins')
                )
                .group_by(BettingCode.category)
                .all()
            )
            
            total_codes = sum(total for _, total, _ in success_rates)
            total_wins = sum(wins for _, _, wins in success_rates)
            
            performance["success_rates"]["overall"] = (
                (total_wins / total_codes * 100) if total_codes > 0 else 0
            )
            
            performance["success_rates"]["by_category"] = {
                cat: (wins / total * 100) if total > 0 else 0
                for cat, total, wins in success_rates if cat is not None
            }
        except Exception as e:
            logger.error(f"Error calculating success rates: {str(e)}")
        
        try:
            # Get popular categories
            popular_categories = (
                db.query(
                    BettingCode.category,
                    func.count(CodePurchase.id).label('purchases')
                )
                .join(CodePurchase, CodePurchase.code_id == BettingCode.id)
                .group_by(BettingCode.category)
                .order_by(func.count(CodePurchase.id).desc())
                .limit(5)
                .all()
            )
            
            performance["popular_categories"] = [
                {"category": cat, "purchases": purchases}
                for cat, purchases in popular_categories if cat is not None
            ]
        except Exception as e:
            logger.error(f"Error getting popular categories: {str(e)}")
        
        return performance
        
    except Exception as e:
        logger.error(f"Error fetching marketplace performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching marketplace performance")

@router.get("/codes/{code_id}/similar")
async def get_similar_codes(
    code_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 5
):
    """Get similar codes based on category, success rate, and price range"""
    try:
        # Get the reference code
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Code not found")
        
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot access codes from other countries")
        
        # Calculate price range (±20%)
        min_price = code.price * 0.8
        max_price = code.price * 1.2
        
        # Find similar codes
        similar_codes = (
            db.query(
                BettingCode,
                func.avg(CodeRating.rating).label('avg_rating'),
                func.count(CodePurchase.id).label('purchase_count')
            )
            .outerjoin(CodeRating, CodeRating.code_id == BettingCode.id)
            .outerjoin(CodePurchase, CodePurchase.code_id == BettingCode.id)
            .filter(
                BettingCode.id != code_id,
                BettingCode.user_country == country,
                BettingCode.is_published == True,
                BettingCode.marketplace_status == 'active',
                BettingCode.category == code.category,
                BettingCode.price.between(min_price, max_price)
            )
            .group_by(BettingCode.id)
            .order_by(
                func.abs(BettingCode.win_probability - code.win_probability),
                func.avg(CodeRating.rating).desc()
            )
            .limit(limit)
            .all()
        )
        
        return [{
            **code.to_dict(),
            'stats': {
                'rating': float(avg_rating) if avg_rating else 0,
                'purchases': purchase_count
            }
        } for code, avg_rating, purchase_count in similar_codes]
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching similar codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching similar codes")

@router.post("/analyze/{code_id}/ai")
async def get_ai_analysis(
    code_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get AI analysis for a betting code"""
    try:
        # Get betting code
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Betting code not found")
            
        # Verify country access
        country = current_admin.country.lower()
        if code.user_country.lower() != country:
            raise HTTPException(status_code=403, detail="Cannot analyze codes from other countries")
        
        # Get AI analysis
        from app.core.ai_analyzer import analyze_betting_code
        analysis = analyze_betting_code(code)
        
        return analysis
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting AI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting AI analysis")

@router.post("/marketplace/admin/upload")
async def admin_upload_to_marketplace(
    upload_data: dict,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Upload a new code directly to marketplace as admin"""
    try:
        country = current_admin.country.lower()
        country_config = get_country_config(country)
        
        # Validate marketplace data
        validate_marketplace_data(upload_data, country_config)
        
        # Validate bookmaker
        bookmaker = next(
            (b for b in country_config["bookmakers"] if b["id"] == upload_data["bookmaker"]),
            None
        )
        if not bookmaker:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid bookmaker for {country}"
            )
        
        # Calculate validity period
        valid_until = datetime.utcnow() + timedelta(hours=int(upload_data.get('validityPeriod', 24)))
        
        # Create new betting code with approved status directly
        code = BettingCode(
            code=upload_data["code"],
            title=upload_data["title"],
            description=upload_data["description"],
            bookmaker=upload_data["bookmaker"],
            user_country=country,
            price=upload_data["price"],
            win_probability=upload_data["winProbability"],
            expected_odds=upload_data["expectedOdds"],
            odds=upload_data["expectedOdds"],
            stake=upload_data["minStake"],
            potential_winnings=upload_data["expectedOdds"] * upload_data["minStake"],
            valid_until=valid_until,
            min_stake=upload_data["minStake"],
            category=upload_data["category"],
            is_published=True,  # Set to True for immediate visibility
            marketplace_status="active",  # Set to active for immediate visibility
            analysis_status="completed",
            issuer=current_admin.full_name,
            issuer_type="admin",
            status="approved",  # Set approved status directly
            verified_at=datetime.utcnow(),
            verified_by=current_admin.id
        )
        
        try:
            # Add and commit in one transaction
            db.add(code)
            db.commit()
            db.refresh(code)
            
            # Return the code with all necessary fields
            return {
                "success": True,
                "message": "Code successfully uploaded to marketplace",
                "code": code.to_dict()
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while uploading code: {str(e)}")
            raise HTTPException(status_code=500, detail="Error saving code to database")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error uploading to marketplace: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error uploading to marketplace")

@router.post("/verify-payment")
async def verify_payment(
    payment_data: dict,
    db: Session = Depends(get_db)
):
    """Verify payment and deliver purchased code"""
    try:
        # Extract payment data
        reference = payment_data.get('reference')
        code_id = payment_data.get('code_id')
        email = payment_data.get('email')
        country = payment_data.get('country', '').lower()
        amount = payment_data.get('amount')
        
        if not all([reference, code_id, email, country]):
            raise HTTPException(
                status_code=400,
                detail="Missing required payment data"
            )

        # Get the code first to verify amount
        code = db.query(BettingCode).filter(BettingCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Code not found")

        # Get country config for Paystack settings
        country_config = get_country_config(country)
        if not country_config:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid country: {country}"
            )

        print(f"Verifying payment for code {code_id}, amount {amount}, reference {reference}")

        # Verify payment with Paystack
        from app.core.payment import verify_paystack_payment
        verification = await verify_paystack_payment(
            reference=reference,
            country_config=country_config,
            expected_amount=code.price  # Pass expected amount for verification
        )
        
        if not verification['success']:
            raise HTTPException(
                status_code=400,
                detail=verification['message']
            )

        print(f"Payment verified successfully for code {code_id}")

        try:
            # Create purchase record
            purchase = CodePurchase(
                code_id=code_id,
                reference=reference,
                email=email,
                amount=amount,
                currency=payment_data.get('currency'),
                country=country,
                payment_method='paystack',
                status='completed'
            )
            
            db.add(purchase)
            
            # Update code status
            code.marketplace_status = 'sold'
            
            db.commit()
            print(f"Purchase record created for code {code_id}")

        except Exception as e:
            db.rollback()
            logger.error(f"Database error saving purchase: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error saving purchase record"
            )

        # Format code details for email
        code_details = {
            'code': code.code,
            'bookmaker': code.bookmaker,
            'win_probability': code.win_probability,
            'expected_odds': code.expected_odds,
            'valid_until': code.valid_until.isoformat() if code.valid_until else None,
            'category': code.category,
            'title': code.title,
            'description': code.description,
            'market_data': code.market_data,
            'price': code.price,
            'min_stake': code.min_stake,
            'tags': code.tags,
            'issuer': code.issuer,
            'issuer_type': code.issuer_type,
            'marketplace_status': code.marketplace_status,
            'analysis_status': code.analysis_status,
            'user_country': code.user_country,
            'email': email  # Include buyer's email
        }

        print(f"Returning code details for {code_id}")
        
        # Return success with code data
        return {
            "success": True,
            "message": "Payment verified successfully",
            "code": code_details
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying payment: {str(e)}"
        ) 