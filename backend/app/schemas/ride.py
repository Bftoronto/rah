from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RideBase(BaseModel):
    from_location: str
    to_location: str
    date: datetime
    price: float
    seats: int

class RideCreate(RideBase):
    pass

class RideRead(RideBase):
    id: int
    driver_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class RideUpdate(BaseModel):
    from_location: Optional[str]
    to_location: Optional[str]
    date: Optional[datetime]
    price: Optional[float]
    seats: Optional[int]

    class Config:
        populate_by_name = True 