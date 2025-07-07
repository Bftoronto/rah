from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging

from ..schemas.payment import PaymentCreate, PaymentRead
from ..services.payment_service import payment_service
from ..services.auth_service import get_current_user
from ..models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process", response_model=PaymentRead)
async def process_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user)
):
    """Обработка платежа (заглушка)"""
    try:
        # Проверка, что пользователь создает платеж за себя
        if payment_data.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Можно создавать платежи только за себя")
        
        payment = payment_service.create_payment(payment_data)
        return payment
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка обработки платежа: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/history", response_model=List[PaymentRead])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Количество платежей"),
    offset: int = Query(0, ge=0, description="Смещение")
):
    """Получение истории платежей пользователя"""
    try:
        payments = payment_service.get_payment_history(current_user.id, limit, offset)
        return payments
        
    except Exception as e:
        logger.error(f"Ошибка получения истории платежей пользователя {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/refund", response_model=PaymentRead)
async def process_refund(
    payment_id: int = Query(..., description="ID платежа"),
    current_user: User = Depends(get_current_user)
):
    """Обработка возврата средств (заглушка)"""
    try:
        payment = payment_service.process_refund(payment_id, current_user.id)
        return payment
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка обработки возврата платежа {payment_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_payment_statistics(
    current_user: User = Depends(get_current_user)
):
    """Получение статистики платежей пользователя"""
    try:
        stats = payment_service.get_payment_statistics(current_user.id)
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики платежей пользователя {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/{payment_id}", response_model=PaymentRead)
async def get_payment(
    payment_id: int = Path(..., description="ID платежа"),
    current_user: User = Depends(get_current_user)
):
    """Получение информации о платеже"""
    try:
        payment = payment_service.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Платеж не найден")
        
        # Проверка прав доступа
        if payment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Нет прав на просмотр этого платежа")
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения платежа {payment_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/ride/{ride_id}/pay", response_model=PaymentRead)
async def pay_for_ride(
    ride_id: int = Path(..., description="ID поездки"),
    current_user: User = Depends(get_current_user)
):
    """Оплата поездки (заглушка)"""
    try:
        # Получение информации о поездке
        from ..services.ride_service import ride_service
        ride = ride_service.get_ride(ride_id)
        
        if not ride:
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        if ride.passenger_id != current_user.id:
            raise HTTPException(status_code=403, detail="Можно оплатить только забронированную поездку")
        
        # Создание платежа
        payment_data = PaymentCreate(
            user_id=current_user.id,
            ride_id=ride_id,
            amount=ride.price
        )
        
        payment = payment_service.create_payment(payment_data)
        return payment
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка оплаты поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера") 