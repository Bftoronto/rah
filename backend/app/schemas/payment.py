from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentBase(BaseModel):
    user_id: int
    ride_id: int
    amount: float
    status: Optional[str] = 'pending'

class PaymentCreate(PaymentBase):
    pass

class PaymentRead(PaymentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None

class PaymentStatistics(BaseModel):
    total_payments: int
    total_amount: float
    refunded_amount: float
    completed_payments: int
    refunded_payments: int 