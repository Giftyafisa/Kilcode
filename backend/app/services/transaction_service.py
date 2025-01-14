from typing import Optional
from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from fastapi import HTTPException, status
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransactionService:
    @staticmethod
    async def create_transaction(
        db: Session,
        user: User,
        transaction_data: TransactionCreate
    ) -> Transaction:
        logger.info(f"=== CREATING TRANSACTION ===")
        logger.info(f"User ID: {user.id}")
        logger.info(f"Initial balance: {user.balance}")
        logger.info(f"Transaction type: {transaction_data.type}")
        logger.info(f"Transaction amount: {transaction_data.amount}")
        
        # Generate unique payment reference
        payment_reference = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate fee based on transaction type and amount
        fee = TransactionService.calculate_fee(
            transaction_data.type,
            transaction_data.amount,
            user.country
        )
        
        logger.info(f"Calculated fee: {fee}")
        
        # Create transaction
        db_transaction = Transaction(
            user_id=user.id,
            type=transaction_data.type,
            amount=transaction_data.amount,
            fee=fee,
            status='completed' if transaction_data.type == 'reward' else 'pending',
            payment_method=transaction_data.payment_method,
            payment_reference=payment_reference,
            description=transaction_data.description,
            currency=transaction_data.currency
        )
        
        db.add(db_transaction)
        logger.info(f"Transaction added to session")
        
        # If it's a reward transaction, update user balance immediately
        if transaction_data.type == 'reward' and db_transaction.status == 'completed':
            old_balance = user.balance
            user.balance += transaction_data.amount
            logger.info(f"=== REWARD BALANCE UPDATE ===")
            logger.info(f"Old balance: {old_balance}")
            logger.info(f"Reward amount: {transaction_data.amount}")
            logger.info(f"New balance (before commit): {user.balance}")
            db.add(user)
        
        try:
            logger.info(f"=== COMMITTING TRANSACTION ===")
            db.commit()
            logger.info(f"=== COMMIT SUCCESSFUL ===")
            
            db.refresh(db_transaction)
            logger.info(f"Transaction refreshed, ID: {db_transaction.id}")
            
            if transaction_data.type == 'reward':
                db.refresh(user)  # Refresh user to get updated balance
                logger.info(f"User refreshed, final balance: {user.balance}")
                
            return db_transaction
        except Exception as e:
            logger.error(f"=== TRANSACTION COMMIT FAILED ===")
            logger.error(f"Error: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create transaction: {str(e)}"
            )

    @staticmethod
    def calculate_fee(type: str, amount: float, country: str) -> float:
        # Fee calculation logic based on country and transaction type
        if country.lower() == 'nigeria':
            if type == 'withdrawal':
                return max(100, amount * 0.015)  # 1.5% or minimum 100 NGN
            return 0
        elif country.lower() == 'ghana':
            if type == 'withdrawal':
                return max(1, amount * 0.01)  # 1% or minimum 1 GHS
            return 0
        return 0

    @staticmethod
    async def process_transaction(
        db: Session,
        transaction_id: int,
        user: User
    ) -> Transaction:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
            
        # Process based on payment method
        if transaction.payment_method == 'paystack':
            await PaystackService.process_payment(transaction)
        elif transaction.payment_method in ['mtn_momo', 'vodafone_cash', 'airtel_money']:
            await MobileMoneyService.process_payment(transaction)
        
        return transaction 

    @staticmethod
    async def update_transaction_status(
        db: Session,
        reference: str,
        status: str,
        payment_data: dict
    ) -> Transaction:
        logger.info(f"=== UPDATING TRANSACTION STATUS ===")
        logger.info(f"Reference: {reference}")
        logger.info(f"New status: {status}")
        
        transaction = db.query(Transaction).filter(
            Transaction.payment_reference == reference
        ).first()
        
        if not transaction:
            logger.error(f"Transaction not found: {reference}")
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        logger.info(f"Found transaction ID: {transaction.id}")
        logger.info(f"Transaction type: {transaction.type}")
        logger.info(f"Transaction amount: {transaction.amount}")
        
        # Get fresh user object
        user = db.query(User).filter(User.id == transaction.user_id).first()
        if not user:
            logger.error(f"User not found: {transaction.user_id}")
            raise HTTPException(status_code=404, detail="User not found")
            
        logger.info(f"Found user ID: {user.id}")
        logger.info(f"Current balance: {user.balance}")
            
        old_status = transaction.status
        transaction.status = status
        transaction.payment_data = payment_data
        
        if status == 'completed' and old_status != 'completed':
            transaction.completed_at = datetime.utcnow()
            logger.info(f"=== PROCESSING COMPLETED TRANSACTION ===")
            
            # Update user balance based on transaction type
            old_balance = user.balance
            
            if transaction.type == 'deposit':
                # Deposits belong to Kilcode, don't add to user balance
                logger.info(f"Processing deposit: (not added to user balance)")
                logger.info(f"Amount: {transaction.amount}")
            elif transaction.type == 'withdrawal':
                total_deduction = transaction.amount + transaction.fee
                if user.balance < total_deduction:
                    logger.error(f"Insufficient balance: {user.balance} < {total_deduction}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient balance for withdrawal including fees"
                    )
                user.balance -= total_deduction
                logger.info(f"Processing withdrawal:")
                logger.info(f"Amount: -{transaction.amount}")
                logger.info(f"Fee: -{transaction.fee}")
            elif transaction.type == 'reward':
                user.balance += transaction.amount
                logger.info(f"Processing reward:")
                logger.info(f"Amount: +{transaction.amount}")
                
            logger.info(f"=== BALANCE UPDATE ===")
            logger.info(f"Old balance: {old_balance}")
            logger.info(f"New balance (before commit): {user.balance}")
                
        try:
            logger.info(f"=== COMMITTING CHANGES ===")
            db.commit()
            logger.info(f"=== COMMIT SUCCESSFUL ===")
            
            db.refresh(transaction)
            logger.info(f"Transaction refreshed")
            
            db.refresh(user)
            logger.info(f"User refreshed, final balance: {user.balance}")
            
            return transaction
        except Exception as e:
            logger.error(f"=== COMMIT FAILED ===")
            logger.error(f"Error: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update transaction status"
            )