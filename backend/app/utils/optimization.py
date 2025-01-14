from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

class QueryOptimizer:
    @staticmethod
    def optimize_betting_code_query(
        db: Session,
        country: str,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Optimized query for fetching betting codes with country-specific indexes
        """
        query = text("""
            SELECT bc.*, u.country
            FROM betting_codes bc
            JOIN users u ON bc.user_id = u.id
            WHERE u.country = :country
            AND bc.user_id = :user_id
            ORDER BY bc.created_at DESC
            LIMIT 100
        """)
        
        result = db.execute(
            query,
            {"country": country, "user_id": user_id}
        )
        
        return [dict(row) for row in result]

    @staticmethod
    def optimize_transaction_query(
        db: Session,
        country: str,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Optimized query for fetching transactions with country-specific indexes
        """
        query = text("""
            SELECT t.*, u.country
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE u.country = :country
            AND t.user_id = :user_id
            ORDER BY t.created_at DESC
            LIMIT 50
        """)
        
        result = db.execute(
            query,
            {"country": country, "user_id": user_id}
        )
        
        return [dict(row) for row in result] 