from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..schemas.ride import RideCreate, RideUpdate, RideRead
from ..services.ride_service import ride_service
from ..services.auth_service import get_current_user
from ..database import get_db
from ..models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=RideRead)
async def create_ride(
    ride_data: RideCreate,
    current_user: User = Depends(get_current_user)
):
    """Создание новой поездки"""
    try:
        ride = ride_service.create_ride(ride_data, current_user.id)
        return ride
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка создания поездки: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_rides(
    from_location: Optional[str] = Query(None, description="Место отправления"),
    to_location: Optional[str] = Query(None, description="Место назначения"),
    date_from: Optional[datetime] = Query(None, description="Дата от (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Дата до (ISO 8601)"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    min_seats: Optional[int] = Query(None, description="Минимальное количество мест"),
    driver_id: Optional[int] = Query(None, description="ID водителя"),
    status: Optional[str] = Query(None, description="Статус поездки"),
    limit: int = Query(50, ge=1, le=100, description="Количество результатов"),
    offset: int = Query(0, ge=0, description="Смещение")
):
    """Поиск поездок с фильтрами"""
    try:
        rides = ride_service.search_rides(
            from_location=from_location,
            to_location=to_location,
            date_from=date_from,
            date_to=date_to,
            max_price=max_price,
            min_seats=min_seats,
            driver_id=driver_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        # Добавление информации о водителе
        rides_with_driver = []
        for ride in rides:
            driver = ride.driver
            ride_dict = {
                "id": ride.id,
                "from_location": ride.from_location,
                "to_location": ride.to_location,
                "date": ride.date,
                "price": ride.price,
                "seats": ride.seats,
                "status": ride.status,
                "created_at": ride.created_at,
                "driver": {
                    "id": driver.id,
                    "full_name": driver.full_name,
                    "average_rating": driver.average_rating,
                    "total_rides": driver.total_rides,
                    "avatar_url": driver.avatar_url
                } if driver else None
            }
            rides_with_driver.append(ride_dict)
        
        return rides_with_driver
        
    except Exception as e:
        logger.error(f"Ошибка поиска поездок: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/{ride_id}", response_model=Dict[str, Any])
async def get_ride(
    ride_id: int = Path(..., description="ID поездки")
):
    """Получение детальной информации о поездке"""
    try:
        ride = ride_service.get_ride(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        driver = ride.driver
        passenger = ride.passenger
        
        ride_details = {
            "id": ride.id,
            "from_location": ride.from_location,
            "to_location": ride.to_location,
            "date": ride.date,
            "price": ride.price,
            "seats": ride.seats,
            "status": ride.status,
            "created_at": ride.created_at,
            "updated_at": ride.updated_at,
            "driver": {
                "id": driver.id,
                "full_name": driver.full_name,
                "average_rating": driver.average_rating,
                "total_rides": driver.total_rides,
                "avatar_url": driver.avatar_url,
                "phone": driver.phone
            } if driver else None,
            "passenger": {
                "id": passenger.id,
                "full_name": passenger.full_name,
                "average_rating": passenger.average_rating,
                "total_rides": passenger.total_rides,
                "avatar_url": passenger.avatar_url
            } if passenger else None
        }
        
        return ride_details
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/{ride_id}/book", response_model=Dict[str, Any])
async def book_ride(
    ride_id: int = Path(..., description="ID поездки"),
    current_user: User = Depends(get_current_user)
):
    """Бронирование поездки"""
    try:
        ride = ride_service.book_ride(ride_id, current_user.id)
        
        return {
            "message": "Поездка успешно забронирована",
            "ride_id": ride.id,
            "status": ride.status,
            "seats_remaining": ride.seats
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка бронирования поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.put("/{ride_id}/cancel", response_model=Dict[str, Any])
async def cancel_ride(
    ride_id: int = Path(..., description="ID поездки"),
    current_user: User = Depends(get_current_user),
    is_driver: bool = Query(False, description="Отмена водителем")
):
    """Отмена поездки"""
    try:
        ride = ride_service.cancel_ride(ride_id, current_user.id, is_driver)
        
        return {
            "message": "Поездка успешно отменена",
            "ride_id": ride.id,
            "status": ride.status,
            "seats_remaining": ride.seats
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка отмены поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.put("/{ride_id}/complete", response_model=Dict[str, Any])
async def complete_ride(
    ride_id: int = Path(..., description="ID поездки"),
    current_user: User = Depends(get_current_user)
):
    """Завершение поездки"""
    try:
        ride = ride_service.complete_ride(ride_id, current_user.id)
        
        return {
            "message": "Поездка успешно завершена",
            "ride_id": ride.id,
            "status": ride.status
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка завершения поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/user/me", response_model=List[Dict[str, Any]])
async def get_my_rides(
    current_user: User = Depends(get_current_user),
    role: str = Query("all", description="Роль: all, driver, passenger")
):
    """Получение поездок текущего пользователя"""
    try:
        rides = ride_service.get_user_rides(current_user.id, role)
        
        rides_with_details = []
        for ride in rides:
            driver = ride.driver
            passenger = ride.passenger
            
            ride_dict = {
                "id": ride.id,
                "from_location": ride.from_location,
                "to_location": ride.to_location,
                "date": ride.date,
                "price": ride.price,
                "seats": ride.seats,
                "status": ride.status,
                "created_at": ride.created_at,
                "driver": {
                    "id": driver.id,
                    "full_name": driver.full_name,
                    "average_rating": driver.average_rating
                } if driver else None,
                "passenger": {
                    "id": passenger.id,
                    "full_name": passenger.full_name,
                    "average_rating": passenger.average_rating
                } if passenger else None
            }
            rides_with_details.append(ride_dict)
        
        return rides_with_details
        
    except Exception as e:
        logger.error(f"Ошибка получения поездок пользователя {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.put("/{ride_id}", response_model=RideRead)
async def update_ride(
    ride_id: int = Path(..., description="ID поездки"),
    ride_data: RideUpdate = ...,
    current_user: User = Depends(get_current_user)
):
    """Обновление поездки"""
    try:
        ride = ride_service.update_ride(ride_id, ride_data, current_user.id)
        return ride
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка обновления поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/user/me/statistics", response_model=Dict[str, Any])
async def get_my_ride_statistics(
    current_user: User = Depends(get_current_user)
):
    """Получение статистики поездок пользователя"""
    try:
        stats = ride_service.get_ride_statistics(current_user.id)
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики пользователя {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.delete("/{ride_id}", response_model=Dict[str, Any])
async def delete_ride(
    ride_id: int = Path(..., description="ID поездки"),
    current_user: User = Depends(get_current_user)
):
    """Удаление поездки (только водителем)"""
    try:
        ride = ride_service.get_ride(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        if ride.driver_id != current_user.id:
            raise HTTPException(status_code=403, detail="Только водитель может удалить поездку")
        
        if ride.status != "active":
            raise HTTPException(status_code=400, detail="Можно удалить только активную поездку")
        
        # Логическое удаление (изменение статуса)
        ride.status = "deleted"
        ride.updated_at = datetime.utcnow()
        
        return {
            "message": "Поездка успешно удалена",
            "ride_id": ride.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера") 