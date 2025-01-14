from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    def get_by_user(self, db: Session, *, user_id: int) -> List[Payment]:
        return db.query(Payment).filter(Payment.user_id == user_id).all()
    
    def get_pending(self, db: Session) -> List[Payment]:
        return db.query(Payment).filter(Payment.status == "pending").all()
    
    def update_status(
        self, db: Session, *, db_obj: Payment, status: str
    ) -> Payment:
        db_obj.status = status
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

payment = CRUDPayment(Payment) 