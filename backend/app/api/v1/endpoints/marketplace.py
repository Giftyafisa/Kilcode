from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict
from sqlalchemy.orm import Session
from app.db.admin_session import get_admin_db
from app.db.session import get_db
from app.models.betting_code import BettingCode
from app.models.code_view import CodeView
from app.models.code_purchase import CodePurchase
from app.models.code_rating import CodeRating
from app.utils.country_utils import get_country_config
from app.utils.marketplace_utils import validate_marketplace_data
from app.core.auth import get_current_admin
from sqlalchemy import func, text
import logging
from datetime import datetime, timedelta

router = APIRouter(
    tags=["marketplace"]
)
logger = logging.getLogger(__name__)

@router.get("/status")
async def get_marketplace_status() -> Dict:
    """Get the current status of the marketplace"""
    try:
        return {
            "status": "online",
            "features": {
                "payments": True,
                "notifications": True,
                "websocket": True
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Error in get_marketplace_status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/codes")
async def get_marketplace_codes(
    country: str,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
    sort_by: str = Query("popularity", regex="^(popularity|date|price)$"),
    db: Session = Depends(get_db)
):
    """Get betting codes available in the marketplace for a specific country. This is a public endpoint."""
    try:
        # Log request details
        logger.info(f"Fetching marketplace codes for country: {country}")
        logger.info(f"Page: {page}, Limit: {limit}, Sort by: {sort_by}")
        
        # Validate country
        country = country.lower()
        try:
            country_config = get_country_config(country)
            if not country_config:
                logger.error(f"Invalid country: {country}")
                raise HTTPException(status_code=400, detail="Invalid country")
        except ValueError as e:
            logger.error(f"Error validating country: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))

        # Calculate offset
        offset = (page - 1) * limit
        logger.info(f"Calculated offset: {offset}")

        try:
            # Build base query for public codes only
            query = db.query(BettingCode).filter(
                BettingCode.is_in_marketplace == True,
                BettingCode.is_published == True,
                BettingCode.user_country == country,
                BettingCode.marketplace_status == 'active'  # Only show active codes
            )
            
            logger.info("Base query built with filters")

            # Apply sorting
            if sort_by == "popularity":
                # Calculate popularity score based on purchases and ratings only
                query = (
                    db.query(
                        BettingCode,
                        (func.count(CodePurchase.id) * 0.7 +  # 70% weight for purchases
                         func.coalesce(func.avg(CodeRating.rating), 0) * 0.3  # 30% weight for ratings
                        ).label('popularity_score')
                    )
                    .outerjoin(CodePurchase, CodePurchase.code_id == BettingCode.id)
                    .outerjoin(CodeRating, CodeRating.code_id == BettingCode.id)
                    .filter(
                        BettingCode.is_in_marketplace == True,
                        BettingCode.is_published == True,
                        BettingCode.user_country == country,
                        BettingCode.marketplace_status == 'active'  # Only show active codes
                    )
                    .group_by(BettingCode.id)
                    .order_by(text('popularity_score DESC'))
                )
                logger.info("Applied popularity sorting")
            elif sort_by == "date":
                query = query.order_by(BettingCode.created_at.desc())
                logger.info("Applied date sorting")
            elif sort_by == "price":
                query = query.order_by(BettingCode.price.asc())
                logger.info("Applied price sorting")

            # Get total count and results
            if sort_by == "popularity":
                # For popularity sort, we already have the query with joins
                total_count = query.count()
                codes = query.offset(offset).limit(limit).all()
                codes = [code[0] for code in codes]  # Extract BettingCode from result tuple
            else:
                # For other sorts, use the simple query
                total_count = query.count()
                codes = query.offset(offset).limit(limit).all()
                
            logger.info(f"Found {total_count} total codes")
            logger.info(f"Returning {len(codes)} codes for current page")

            # Convert to dict and filter sensitive data
            codes_data = [{
                'id': code.id,
                'bookmaker': code.bookmaker,
                'title': code.title,
                'description': code.description,
                'price': code.price,
                'win_probability': code.win_probability,
                'expected_odds': code.expected_odds,
                'min_stake': code.min_stake,
                'category': code.category,
                'marketplace_status': code.marketplace_status,
                'valid_until': code.valid_until.isoformat() if code.valid_until else None,
                'created_at': code.created_at.isoformat() if code.created_at else None
            } for code in codes]

            response_data = {
                "success": True,
                "data": {
                    "codes": codes_data,
                    "total": total_count,
                    "page": page,
                    "limit": limit,
                    "total_pages": (total_count + limit - 1) // limit
                }
            }
            
            logger.info(f"Successfully prepared response with {len(codes_data)} codes")
            return response_data
            
        except Exception as e:
            logger.error(f"Database error in get_marketplace_codes: {str(e)}")
            raise HTTPException(status_code=500, detail="Error accessing database")
            
    except HTTPException as e:
        logger.error(f"HTTP Exception in get_marketplace_codes: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error fetching marketplace codes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching marketplace codes")

@router.post("/admin/upload")
async def upload_to_marketplace(
    data: Dict,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_admin_db)
):
    """Upload a betting code to the marketplace"""
    try:
        # Log the upload attempt and data
        logger.info(f"Admin {current_admin.email} attempting to upload code to marketplace")
        logger.info(f"Upload data received: {data}")
        logger.info(f"Admin details - ID: {current_admin.id}, Country: {current_admin.country}")
        
        # Get country from admin object
        if not current_admin.country:
            logger.error("No country set for admin")
            raise HTTPException(
                status_code=400,
                detail="No country set for admin"
            )
            
        country = current_admin.country.lower()
        logger.info(f"Getting country config for {country}")
        
        # Verify country is valid
        if country not in ['ghana', 'nigeria']:
            logger.error(f"Invalid country: {country}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid country: {country}"
            )
        
        try:
            # Get country config with detailed logging
            logger.info(f"Fetching config for country: {country}")
            country_config = get_country_config(country)
            logger.info(f"Country config keys: {country_config.keys() if country_config else None}")
            logger.info(f"Country name from config: {country_config.get('name') if country_config else None}")
            
            if not country_config:
                logger.error(f"No configuration found for country: {country}")
                raise HTTPException(
                    status_code=400,
                    detail=f"No configuration found for country: {country}"
                )
                
            # Log country config for debugging
            logger.info(f"Country config retrieved: {country_config.get('name', 'Unknown')}")
                
            # Verify marketplace settings exist
            marketplace_settings = country_config.get('marketplace_settings', {})
            if not marketplace_settings:
                logger.error(f"No marketplace settings found for country: {country}")
                raise HTTPException(
                    status_code=400,
                    detail=f"No marketplace settings configured for {country}"
                )
                
            # Log marketplace settings for debugging
            logger.info(f"Marketplace settings found: {marketplace_settings}")
                
            # Verify categories exist
            categories = marketplace_settings.get('categories', [])
            if not categories:
                logger.error(f"No categories found for country: {country}")
                raise HTTPException(
                    status_code=400,
                    detail=f"No categories configured for {country}"
                )
                
            # Log categories for debugging
            logger.info(f"Available categories: {categories}")
                
        except ValueError as e:
            logger.error(f"Error getting country config: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # Validate marketplace data
        logger.info(f"Validating marketplace data for country: {country}")
        try:
            validate_marketplace_data(data, country_config)
            logger.info("Marketplace data validation successful")
        except HTTPException as e:
            logger.error(f"Marketplace data validation failed: {str(e.detail)}")
            raise e
        
        # Create betting code
        logger.info("Creating betting code")
        try:
            # Calculate validity period
            validity_hours = int(data.get('validityPeriod', 24))
            valid_until = datetime.utcnow() + timedelta(hours=validity_hours)
            
            # Log all fields before creating object
            code_data = {
                'code': data['code'],
                'title': data['title'],
                'description': data['description'],
                'price': float(data['price']),
                'bookmaker': data['bookmaker'],
                'win_probability': float(data['winProbability']),
                'expected_odds': float(data['expectedOdds']),
                'min_stake': float(data['minStake']),
                'category': data['category'],
                'user_country': country,
                'issuer': current_admin.email,
                'issuer_type': 'admin',
                'marketplace_status': 'active',
                'is_in_marketplace': True,
                'is_published': True,
                'valid_until': valid_until,
                'tags': data.get('tags', []),
                'user_id': current_admin.id,
                'verified_by': current_admin.id,
                'verified_at': datetime.utcnow(),
                'status': 'approved',
                'admin_note': "Uploaded directly by admin",
                'odds': float(data['expectedOdds']),
                'stake': float(data['minStake']),
                'potential_winnings': float(data['expectedOdds']) * float(data['minStake'])
            }
            logger.info(f"Creating BettingCode with data: {code_data}")
            
            code = BettingCode(**code_data)
            
            # Log the code object before adding
            logger.info(f"Created BettingCode object: {code.to_dict()}")
            
            db.add(code)
            logger.info("Added code to session, preparing to commit")
            
            db.commit()
            logger.info("Successfully committed code to database")
            
            db.refresh(code)
            logger.info(f"Refreshed code object, ID: {code.id}")
            
            # Verify the code was saved
            saved_code = db.query(BettingCode).filter(BettingCode.id == code.id).first()
            if saved_code:
                logger.info(f"Successfully verified code in database with ID: {saved_code.id}")
                logger.info(f"Saved code data: {saved_code.to_dict()}")
            else:
                logger.error("Code not found in database after commit!")
                raise HTTPException(
                    status_code=500,
                    detail="Code was not saved properly"
                )
            
            return {
                "success": True,
                "message": "Code uploaded successfully",
                "code": code.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating betting code: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create betting code: {str(e)}"
            )
            
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in upload_to_marketplace: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 

@router.get("/debug/table-info")
async def get_table_info(
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_admin_db)
):
    """Debug endpoint to check betting_codes table structure and data"""
    try:
        # Get table info
        result = db.execute(text("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'betting_codes'
            ORDER BY ordinal_position;
        """))
        columns = [dict(row) for row in result]
        
        # Get sample data
        codes = db.query(BettingCode).limit(5).all()
        sample_data = [code.to_dict() for code in codes]
        
        # Get total count
        total_count = db.query(BettingCode).count()
        
        return {
            "success": True,
            "table_structure": columns,
            "total_records": total_count,
            "sample_data": sample_data
        }
        
    except Exception as e:
        logger.error(f"Error getting table info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting table info: {str(e)}"
        ) 