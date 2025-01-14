from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from typing import List
import logging
from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse,TransactionListResponse
from app.services.transaction_service import TransactionService
from app.models.transaction import Transaction
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

async def force_balance_reset(db: Session, user_id: int) -> float:
    """Force reset user balance using direct SQL queries"""
    try:
        # Log current state
        logger.info("=== FORCE BALANCE RESET STARTED ===")
        
        # Get current user info
        user = db.query(User).filter(User.id == user_id).first()
        logger.info(f"Current user balance: {user.balance}")
        
        # Get all transactions using direct SQL for detailed logging
        sql = text("""
            SELECT id, type, amount, fee, status, payment_reference, created_at, description
            FROM transactions
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)
        result = db.execute(sql, {"user_id": user_id})
        
        logger.info("=== ALL TRANSACTIONS ===")
        all_transactions = []
        total_amount = 0
        for row in result:
            txn = dict(row)
            all_transactions.append(txn)
            
            # Calculate running total
            if txn['type'] == 'reward' and txn['status'] == 'completed':
                total_amount += txn['amount']
            elif txn['type'] == 'withdrawal' and txn['status'] == 'completed':
                total_amount -= (txn['amount'] + (txn['fee'] or 0))
                
            logger.info(f"""
Transaction found:
    ID: {row.id}
    Type: {row.type}
    Amount: {row.amount}
    Fee: {row.fee}
    Status: {row.status}
    Reference: {row.payment_reference}
    Created: {row.created_at}
    Description: {row.description}
Running total: {total_amount}
            """)
        
        # Calculate rewards using direct SQL
        sql_rewards = text("""
            SELECT COALESCE(SUM(amount), 0) as total_rewards
            FROM transactions
            WHERE user_id = :user_id
            AND type = 'reward'
            AND status = 'completed'
        """)
        result = db.execute(sql_rewards, {"user_id": user_id})
        total_rewards = result.scalar() or 0
        logger.info(f"Total rewards from SQL: {total_rewards}")
        
        # Calculate withdrawals using direct SQL
        sql_withdrawals = text("""
            SELECT COALESCE(SUM(amount + COALESCE(fee, 0)), 0) as total_withdrawals
            FROM transactions
            WHERE user_id = :user_id
            AND type = 'withdrawal'
            AND status = 'completed'
        """)
        result = db.execute(sql_withdrawals, {"user_id": user_id})
        total_withdrawals = result.scalar() or 0
        logger.info(f"Total withdrawals from SQL: {total_withdrawals}")
        
        # Calculate correct balance
        correct_balance = total_rewards - total_withdrawals
        logger.info(f"Calculated correct balance: {correct_balance}")
        
        # Double-check against running total
        if abs(correct_balance - total_amount) > 0.01:
            logger.error(f"Balance calculation mismatch! SQL sum: {correct_balance}, Running total: {total_amount}")
        
        # Always update balance to ensure it's correct
        logger.info(f"Updating balance from {user.balance} to {correct_balance}")
        
        # First update using SQLAlchemy
        user.balance = correct_balance
        db.add(user)
        db.commit()
        
        # Then update using direct SQL as backup
        sql_update = text("""
            UPDATE users
            SET balance = :new_balance
            WHERE id = :user_id
        """)
        db.execute(sql_update, {
            "new_balance": correct_balance,
            "user_id": user_id
        })
        db.commit()
        
        # Verify the update with both methods
        user = db.query(User).filter(User.id == user_id).first()
        sql_verify = text("SELECT balance FROM users WHERE id = :user_id")
        sql_balance = db.execute(sql_verify, {"user_id": user_id}).scalar()
        
        logger.info(f"Balance after update (ORM): {user.balance}")
        logger.info(f"Balance after update (SQL): {sql_balance}")
        
        if abs(user.balance - correct_balance) > 0.01 or abs(sql_balance - correct_balance) > 0.01:
            logger.error("Balance update failed! Values don't match!")
            logger.error(f"ORM balance: {user.balance}")
            logger.error(f"SQL balance: {sql_balance}")
            logger.error(f"Expected balance: {correct_balance}")
        
        return correct_balance
            
    except Exception as e:
        logger.error(f"Error in force_balance_reset: {str(e)}")
        db.rollback()
        raise

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await TransactionService.create_transaction(db, current_user, transaction_data)

@router.get("/", response_model=TransactionListResponse)
async def get_user_transactions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info("\n=== GET USER TRANSACTIONS START ===")
        
        # Get fresh user object using direct SQL
        sql_user = text("""
            SELECT id, email, balance, is_verified, payment_status, created_at
            FROM users
            WHERE id = :user_id
        """)
        user_result = db.execute(sql_user, {"user_id": current_user.id}).first()
        
        logger.info("\n=== USER INFO (FROM SQL) ===")
        logger.info(f"""
User details:
    ID: {user_result.id}
    Email: {user_result.email}
    Balance: {user_result.balance}
    Is Verified: {user_result.is_verified}
    Payment Status: {user_result.payment_status}
    Created At: {user_result.created_at}
        """)
        
        # Get all transactions using direct SQL
        sql_transactions = text("""
            SELECT id, type, amount, fee, status, payment_reference, created_at, description
            FROM transactions
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)
        txn_results = db.execute(sql_transactions, {"user_id": current_user.id}).fetchall()
        
        logger.info("\n=== ALL TRANSACTIONS (FROM SQL) ===")
        logger.info(f"Total transactions found: {len(txn_results)}")
        
        total_rewards = 0
        total_withdrawals = 0
        
        for txn in txn_results:
            logger.info(f"""
Transaction:
    ID: {txn.id}
    Type: {txn.type}
    Amount: {txn.amount}
    Fee: {txn.fee}
    Status: {txn.status}
    Reference: {txn.payment_reference}
    Created: {txn.created_at}
    Description: {txn.description}
            """)
            
            if txn.type == 'reward' and txn.status == 'completed':
                total_rewards += txn.amount
            elif txn.type == 'withdrawal' and txn.status == 'completed':
                total_withdrawals += (txn.amount + (txn.fee or 0))
        
        expected_balance = total_rewards - total_withdrawals
        
        logger.info("\n=== BALANCE CALCULATION (FROM SQL) ===")
        logger.info(f"Total Rewards: {total_rewards}")
        logger.info(f"Total Withdrawals: {total_withdrawals}")
        logger.info(f"Expected Balance: {expected_balance}")
        logger.info(f"Current Balance: {user_result.balance}")
        
        # If balance is wrong, force update using direct SQL
        if abs(user_result.balance - expected_balance) > 0.01:
            logger.error(f"\n=== BALANCE MISMATCH DETECTED ===")
            logger.error(f"Current balance ({user_result.balance}) != Expected balance ({expected_balance})")
            
            # Update balance using direct SQL
            sql_update = text("""
                UPDATE users 
                SET balance = :balance 
                WHERE id = :id
            """)
            db.execute(sql_update, {"balance": expected_balance, "id": current_user.id})
            db.commit()
            
            # Verify the update
            verify_result = db.execute(sql_user, {"user_id": current_user.id}).first()
            logger.info(f"\nBalance after SQL update: {verify_result.balance}")
            
            # Get fresh user object for response
            fresh_user = db.query(User).filter(User.id == current_user.id).first()
        else:
            fresh_user = db.query(User).filter(User.id == current_user.id).first()
        
        # Get transactions for response
        transactions = db.query(Transaction)\
            .filter(Transaction.user_id == current_user.id)\
            .order_by(Transaction.created_at.desc())\
            .all()
        
        # Log the final response
        logger.info("\n=== SENDING RESPONSE ===")
        logger.info(f"Final balance being sent: {fresh_user.balance}")
        logger.info(f"Number of transactions: {len(transactions)}")
        
        return {
            "transactions": transactions,
            "balance": fresh_user.balance
        }
        
    except Exception as e:
        logger.error("\n=== ERROR IN GET USER TRANSACTIONS ===")
        logger.error(str(e))
        logger.error("Stack trace:", exc_info=True)
        raise

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction)\
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction 