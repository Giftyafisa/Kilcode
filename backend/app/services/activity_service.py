from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate
from datetime import datetime, timedelta
from app.core.websocket_manager import manager

class ActivityService:
    @staticmethod
    async def create_activity(
        db: Session,
        user_id: int,
        activity_type: str,
        description: str,
        metadata: Dict[str, Any],
        country: str,
        status: str = "success",
        notify: bool = True
    ) -> Activity:
        """Create a new activity record and optionally notify relevant parties"""
        activity_in = ActivityCreate(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            activity_metadata=metadata,
            country=country,
            status=status
        )
        
        activity = Activity(
            user_id=activity_in.user_id,
            activity_type=activity_in.activity_type,
            description=activity_in.description,
            activity_metadata=activity_in.activity_metadata,
            country=activity_in.country,
            status=activity_in.status
        )
        
        db.add(activity)
        db.commit()
        db.refresh(activity)

        if notify:
            # Notify user
            await manager.notify_user(
                user_id=user_id,
                message={
                    "type": "activity",
                    "activity_type": activity_type,
                    "description": description,
                    "status": status,
                    "created_at": activity.created_at.isoformat()
                }
            )

            # Notify country admins if needed
            if activity_type in ["betting_code", "payment", "withdrawal"]:
                await manager.notify_admin_activity(
                    country=country,
                    activity={
                        "id": activity.id,
                        "type": activity_type,
                        "user_id": user_id,
                        "description": description,
                        "status": status,
                        "metadata": activity.activity_metadata,
                        "created_at": activity.created_at.isoformat()
                    }
                )
        
        return activity

    @staticmethod
    def get_user_activities(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        activity_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Activity]:
        """Get activities for a specific user with filters"""
        query = db.query(Activity).filter(Activity.user_id == user_id)
        
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        if status:
            query = query.filter(Activity.status == status)
            
        if start_date:
            query = query.filter(Activity.created_at >= start_date)
            
        if end_date:
            query = query.filter(Activity.created_at <= end_date)
        
        return query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_country_activities(
        db: Session,
        country: str,
        skip: int = 0,
        limit: int = 10,
        activity_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Activity]:
        """Get activities for a specific country with filters"""
        query = db.query(Activity).filter(Activity.country == country)
        
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
            
        if status:
            query = query.filter(Activity.status == status)
            
        if start_date:
            query = query.filter(Activity.created_at >= start_date)
            
        if end_date:
            query = query.filter(Activity.created_at <= end_date)
        
        return query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_recent_activities(
        db: Session,
        country: str,
        hours: int = 24
    ) -> List[Activity]:
        """Get recent activities within specified hours"""
        start_time = datetime.utcnow() - timedelta(hours=hours)
        return db.query(Activity).filter(
            and_(
                Activity.country == country,
                Activity.created_at >= start_time
            )
        ).order_by(Activity.created_at.desc()).all()

    @staticmethod
    def get_activity_summary(
        db: Session,
        user_id: Optional[int] = None,
        country: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get activity summary for user or country"""
        start_date = datetime.utcnow() - timedelta(days=days)
        query = db.query(Activity)

        if user_id:
            query = query.filter(Activity.user_id == user_id)
        if country:
            query = query.filter(Activity.country == country)

        query = query.filter(Activity.created_at >= start_date)
        activities = query.all()

        return {
            "total_activities": len(activities),
            "by_type": {
                activity_type: len([a for a in activities if a.activity_type == activity_type])
                for activity_type in set(a.activity_type for a in activities)
            },
            "by_status": {
                status: len([a for a in activities if a.status == status])
                for status in set(a.status for a in activities)
            },
            "recent_activities": activities[:5]  # Last 5 activities
        }

activity_service = ActivityService() 