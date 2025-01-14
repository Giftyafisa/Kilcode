from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, ForeignKey, Text
from app.core.config import settings
from app.db.base import Base
from app.models.betting_code import BettingCode
from app.models.admin import Admin
from datetime import datetime

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Add columns to betting_codes table
def add_verification_fields():
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Get the betting_codes table
    betting_codes = metadata.tables['betting_codes']
    
    # Add new columns if they don't exist
    columns_to_add = [
        Column('verified_by', Integer, ForeignKey('admins.id', ondelete='SET NULL'), nullable=True),
        Column('admin_note', Text, nullable=True),
        Column('rejection_reason', String, nullable=True),
        Column('verified_at', DateTime(timezone=True), nullable=True)
    ]
    
    with engine.begin() as conn:
        for column in columns_to_add:
            if column.name not in betting_codes.columns:
                conn.execute(f'ALTER TABLE betting_codes ADD COLUMN {column.name} {column.type}')
                print(f"Added column {column.name}")

if __name__ == "__main__":
    add_verification_fields() 