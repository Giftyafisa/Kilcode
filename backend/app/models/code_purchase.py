from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class CodePurchase(Base):
    __tablename__ = "code_purchases"

    id = Column(Integer, primary_key=True, index=True)
    code_id = Column(Integer, ForeignKey("betting_codes.id", ondelete="CASCADE"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, nullable=False, default="completed")
    purchased_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    email = Column(String, nullable=True)
    reference = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    country = Column(String, nullable=True)

    betting_code = relationship("BettingCode", back_populates="purchases")
    buyer = relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "code_id": self.code_id,
            "buyer_id": self.buyer_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "purchased_at": self.purchased_at.isoformat() if self.purchased_at else None,
            "email": self.email,
            "reference": self.reference,
            "payment_method": self.payment_method,
            "country": self.country
        } 