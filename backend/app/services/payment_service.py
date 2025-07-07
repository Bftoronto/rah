from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..models.payment import Payment
from ..models.user import User
from ..models.ride import Ride
from ..schemas.payment import PaymentCreate, PaymentRead
from ..database import get_db

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        self.db: Session = next(get_db())
    
    def create_payment(self, payment_data: PaymentCreate) -> Payment:
        """Создание платежа (заглушка)"""
        try:
            # Проверка пользователя
            user = self.db.query(User).filter(User.id == payment_data.user_id).first()
            if not user:
                raise ValueError("Пользователь не найден")
            
            # Проверка поездки
            ride = self.db.query(Ride).filter(Ride.id == payment_data.ride_id).first()
            if not ride:
                raise ValueError("Поездка не найдена")
            
            # Создание платежа (заглушка)
            payment = Payment(
                user_id=payment_data.user_id,
                ride_id=payment_data.ride_id,
                amount=payment_data.amount,
                status="completed"  # Автоматически завершен для демо
            )
            
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)
            
            logger.info(f"Создан платеж {payment.id} для поездки {payment_data.ride_id}")
            return payment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания платежа: {e}")
            raise
    
    def get_payment_history(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Payment]:
        """Получение истории платежей пользователя"""
        try:
            payments = self.db.query(Payment).filter(
                Payment.user_id == user_id
            ).order_by(Payment.created_at.desc()).limit(limit).offset(offset).all()
            
            return payments
            
        except Exception as e:
            logger.error(f"Ошибка получения истории платежей пользователя {user_id}: {e}")
            raise
    
    def process_refund(self, payment_id: int, user_id: int) -> Payment:
        """Обработка возврата средств (заглушка)"""
        try:
            payment = self.db.query(Payment).filter(
                Payment.id == payment_id
            ).first()
            
            if not payment:
                raise ValueError("Платеж не найден")
            
            if payment.user_id != user_id:
                raise ValueError("Нет прав на возврат этого платежа")
            
            if payment.status != "completed":
                raise ValueError("Можно вернуть только завершенные платежи")
            
            # Создание возврата (заглушка)
            payment.status = "refunded"
            payment.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(payment)
            
            logger.info(f"Обработан возврат для платежа {payment_id}")
            return payment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка обработки возврата платежа {payment_id}: {e}")
            raise
    
    def get_payment_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики платежей пользователя"""
        try:
            payments = self.db.query(Payment).filter(Payment.user_id == user_id).all()
            
            stats = {
                "total_payments": len(payments),
                "total_amount": sum([p.amount for p in payments if p.status == "completed"]),
                "refunded_amount": sum([p.amount for p in payments if p.status == "refunded"]),
                "completed_payments": len([p for p in payments if p.status == "completed"]),
                "refunded_payments": len([p for p in payments if p.status == "refunded"])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики платежей пользователя {user_id}: {e}")
            raise
    
    def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Получение платежа по ID"""
        try:
            payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
            return payment
        except Exception as e:
            logger.error(f"Ошибка получения платежа {payment_id}: {e}")
            raise

# Создание экземпляра сервиса
payment_service = PaymentService() 