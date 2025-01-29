from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.api import deps
from app.models.notification import Notification
from app.core.auth import get_current_user
from app.services.notification_service import send_code_purchase_email
from typing import List, Dict, Any

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_notifications(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(deps.get_db),
    current_user = Depends(get_current_user)
):
    """Get user notifications with pagination"""
    print(f"Fetching notifications for user {current_user.id}")  # Debug log
    
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    print(f"Found {len(notifications)} notifications")  # Debug log
    
    result = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "data": n.notification_data,
            "read": n.read,
            "created_at": n.created_at
        } for n in notifications
    ]
    print(f"Returning notifications: {result}")  # Debug log
    return result

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.read = True
    db.commit()
    
    return {"success": True}

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(deps.get_db),
    current_user = Depends(get_current_user)
):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).count()
    
    return {"unread_count": count}

@router.put("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(deps.get_db),
    current_user = Depends(get_current_user)
):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).update({"read": True})
    
    db.commit()
    return {"success": True}

@router.post("/marketplace/send-purchase-email")
async def send_purchase_email(
    data: Dict[str, Any] = Body(...),
    db: Session = Depends(deps.get_db)
):
    """Send email with purchased code details"""
    try:
        # Validate input data
        if not data.get("email"):
            raise HTTPException(
                status_code=400,
                detail="Email address is required"
            )
        
        if not data.get("code"):
            raise HTTPException(
                status_code=400,
                detail="Code details are required"
            )
        
        # Log the attempt
        print(f"Attempting to send purchase email to: {data['email']}")
        print(f"Code details: {data['code']}")
        
        # Send the email
        email_sent = send_code_purchase_email(
            to_email=data["email"],
            code_details=data["code"]
        )
        
        if email_sent:
            print(f"Successfully sent purchase email to {data['email']}")
            return {"success": True, "message": "Email sent successfully"}
        else:
            print(f"Failed to send purchase email to {data['email']}")
            raise HTTPException(
                status_code=500,
                detail="Failed to send email. Please check server logs for details."
            )
    except HTTPException as he:
        print(f"HTTP error sending purchase email: {str(he)}")
        raise he
    except Exception as e:
        print(f"Unexpected error sending purchase email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        ) 