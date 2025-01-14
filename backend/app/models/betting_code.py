from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, CheckConstraint, Enum, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from sqlalchemy.ext.declarative import declared_attr
import app.models.code_analysis as code_analysis_model  # Import at module level

class BettingCode(Base):
    __tablename__ = "betting_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Allow null for admin uploads
    bookmaker = Column(String, nullable=False)
    code = Column(String, nullable=False)
    odds = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    potential_winnings = Column(Float, nullable=False)
    status = Column(Enum('pending', 'won', 'lost', 'analyzing', 'approved', 'rejected', name='status_types'), default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(Text, nullable=True)
    
    # Admin verification fields
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    admin_note = Column(Text, nullable=True)
    rejection_reason = Column(String, nullable=True)

    # Market data
    market_data = Column(JSON, nullable=True)  # Store additional market data
    price = Column(Float, nullable=True)  # Price when listed on marketplace
    win_probability = Column(Float, nullable=True)  # Probability of winning
    expected_odds = Column(Float, nullable=True)  # Expected odds for the bet
    valid_until = Column(DateTime(timezone=True), nullable=True)  # Validity period
    min_stake = Column(Float, nullable=True)  # Minimum stake required
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # New marketplace fields
    title = Column(String(100), nullable=True)  # Title for marketplace listing
    category = Column(String(50), nullable=True)  # Category (e.g., Football, Basketball)
    issuer = Column(String(100), nullable=True)  # Name of the issuer
    issuer_type = Column(String(20), nullable=True)  # Type of issuer (admin/user)
    marketplace_status = Column(String(20), nullable=True)  # Status in marketplace
    analysis_status = Column(String(20), nullable=True)  # Analysis status
    user_country = Column(String(50), nullable=True)  # Country of the user/admin
    is_published = Column(Boolean, default=False)  # Whether published to marketplace

    # Relationships
    user = relationship("User", back_populates="betting_codes")
    admin = relationship("Admin", back_populates="verified_codes")
    analysis = relationship("CodeAnalysis", back_populates="betting_code", uselist=False)
    views = relationship("CodeView", back_populates="betting_code")
    purchases = relationship("CodePurchase", back_populates="betting_code")
    ratings = relationship("CodeRating", back_populates="betting_code")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bookmaker': self.bookmaker,
            'code': self.code,
            'odds': self.odds,
            'stake': self.stake,
            'potential_winnings': self.potential_winnings,
            'status': self.status,
            'created_at': self.created_at,
            'description': self.description,
            'verified_at': self.verified_at,
            'verified_by': self.verified_by,
            'admin_note': self.admin_note,
            'rejection_reason': self.rejection_reason,
            'market_data': self.market_data,
            'price': self.price,
            'win_probability': self.win_probability,
            'expected_odds': self.expected_odds,
            'valid_until': self.valid_until,
            'min_stake': self.min_stake,
            'tags': self.tags,
            'title': self.title,
            'category': self.category,
            'issuer': self.issuer,
            'issuer_type': self.issuer_type,
            'marketplace_status': self.marketplace_status,
            'analysis_status': self.analysis_status,
            'user_country': self.user_country,
            'analysis': self.analysis.to_dict() if self.analysis else None
        }
    
    # Constraints
    __table_args__ = (
        CheckConstraint('odds >= 1.0', name='check_odds_positive'),
        CheckConstraint('stake > 0', name='check_stake_positive'),
        CheckConstraint('potential_winnings >= stake', name='check_potential_winnings'),
        CheckConstraint('win_probability >= 0 AND win_probability <= 100', name='check_win_probability'),
        CheckConstraint('expected_odds >= 1.0', name='check_expected_odds'),
        CheckConstraint('min_stake >= 0', name='check_min_stake'),
    )