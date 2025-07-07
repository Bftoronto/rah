from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException, status

from ..models.ride import Ride
from ..models.user import User
from ..schemas.ride import RideCreate, RideUpdate, RideRead
from ..utils.validators import validate_ride_data
from ..database import get_db

logger = logging.getLogger(__name__)

class RideService:
    def __init__(self):
        self.db: Session = next(get_db())

    def create_ride(self, ride_data: RideCreate, driver_id: int) -> Ride:
        """Создание новой поездки"""
        try:
            # Проверка, что водитель существует и активен
            driver = self.db.query(User).filter(
                and_(User.id == driver_id, User.is_active == True)
            ).first()
            
            if not driver:
                raise ValueError("Водитель не найден или неактивен")
            
            # Валидация данных поездки
            if ride_data.seats <= 0 or ride_data.seats > 8:
                raise ValueError("Количество мест должно быть от 1 до 8")
            
            if ride_data.price <= 0:
                raise ValueError("Цена должна быть больше 0")
            
            if ride_data.date <= datetime.utcnow():
                raise ValueError("Дата поездки должна быть в будущем")
            
            # Создание поездки
            ride = Ride(
                driver_id=driver_id,
                from_location=ride_data.from_location,
                to_location=ride_data.to_location,
                date=ride_data.date,
                price=ride_data.price,
                seats=ride_data.seats,
                status="active"
            )
            
            self.db.add(ride)
            self.db.commit()
            self.db.refresh(ride)
            
            logger.info(f"Создана поездка {ride.id} водителем {driver_id}")
            return ride
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания поездки: {e}")
            raise

    def get_ride(self, ride_id: int) -> Optional[Ride]:
        """Получение поездки по ID"""
        try:
            ride = self.db.query(Ride).filter(Ride.id == ride_id).first()
            return ride
        except Exception as e:
            logger.error(f"Ошибка получения поездки {ride_id}: {e}")
            raise

    def search_rides(self, 
                    from_location: Optional[str] = None,
                    to_location: Optional[str] = None,
                    date_from: Optional[datetime] = None,
                    date_to: Optional[datetime] = None,
                    max_price: Optional[float] = None,
                    min_seats: Optional[int] = None,
                    driver_id: Optional[int] = None,
                    status: Optional[str] = None,
                    limit: int = 50,
                    offset: int = 0) -> List[Ride]:
        """Поиск поездок с фильтрами"""
        try:
            query = self.db.query(Ride).filter(Ride.status == "active")
            
            # Фильтры
            if from_location:
                query = query.filter(Ride.from_location.ilike(f"%{from_location}%"))
            
            if to_location:
                query = query.filter(Ride.to_location.ilike(f"%{to_location}%"))
            
            if date_from:
                query = query.filter(Ride.date >= date_from)
            
            if date_to:
                query = query.filter(Ride.date <= date_to)
            
            if max_price:
                query = query.filter(Ride.price <= max_price)
            
            if min_seats:
                query = query.filter(Ride.seats >= min_seats)
            
            if driver_id:
                query = query.filter(Ride.driver_id == driver_id)
            
            if status:
                query = query.filter(Ride.status == status)
            
            # Сортировка по дате (ближайшие сначала)
            query = query.order_by(asc(Ride.date))
            
            # Пагинация
            rides = query.limit(limit).offset(offset).all()
            
            return rides
            
        except Exception as e:
            logger.error(f"Ошибка поиска поездок: {e}")
            raise

    def book_ride(self, ride_id: int, passenger_id: int) -> Ride:
        """Бронирование поездки"""
        try:
            # Получение поездки
            ride = self.get_ride(ride_id)
            if not ride:
                raise ValueError("Поездка не найдена")
            
            # Проверка статуса
            if ride.status != "active":
                raise ValueError("Поездка недоступна для бронирования")
            
            # Проверка, что пассажир не является водителем
            if ride.driver_id == passenger_id:
                raise ValueError("Водитель не может забронировать свою поездку")
            
            # Проверка пассажира
            passenger = self.db.query(User).filter(
                and_(User.id == passenger_id, User.is_active == True)
            ).first()
            
            if not passenger:
                raise ValueError("Пассажир не найден или неактивен")
            
            # Проверка доступности мест
            if ride.seats <= 0:
                raise ValueError("Нет свободных мест")
            
            # Бронирование
            ride.passenger_id = passenger_id
            ride.seats -= 1
            ride.status = "booked"
            ride.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(ride)
            
            logger.info(f"Поездка {ride_id} забронирована пассажиром {passenger_id}")
            return ride
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка бронирования поездки {ride_id}: {e}")
            raise

    def cancel_ride(self, ride_id: int, user_id: int, is_driver: bool = False) -> Ride:
        """Отмена поездки"""
        try:
            ride = self.get_ride(ride_id)
            if not ride:
                raise ValueError("Поездка не найдена")
            
            # Проверка прав на отмену
            if is_driver:
                if ride.driver_id != user_id:
                    raise ValueError("Только водитель может отменить поездку")
            else:
                if ride.passenger_id != user_id:
                    raise ValueError("Только пассажир может отменить бронь")
            
            # Проверка возможности отмены (не менее чем за 2 часа)
            if ride.date - datetime.utcnow() < timedelta(hours=2):
                raise ValueError("Отмена возможна не менее чем за 2 часа до поездки")
            
            # Отмена
            if is_driver:
                ride.status = "cancelled"
                # Возврат места пассажиру, если был
                if ride.passenger_id:
                    ride.seats += 1
                    ride.passenger_id = None
            else:
                # Отмена брони пассажиром
                ride.passenger_id = None
                ride.seats += 1
                ride.status = "active"
            
            ride.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(ride)
            
            logger.info(f"Поездка {ride_id} отменена пользователем {user_id}")
            return ride
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка отмены поездки {ride_id}: {e}")
            raise

    def complete_ride(self, ride_id: int, driver_id: int) -> Ride:
        """Завершение поездки"""
        try:
            ride = self.get_ride(ride_id)
            if not ride:
                raise ValueError("Поездка не найдена")
            
            if ride.driver_id != driver_id:
                raise ValueError("Только водитель может завершить поездку")
            
            if ride.status not in ["active", "booked"]:
                raise ValueError("Поездка уже завершена или отменена")
            
            ride.status = "completed"
            ride.updated_at = datetime.utcnow()
            
            # Обновление статистики пользователей
            driver = self.db.query(User).filter(User.id == driver_id).first()
            if driver:
                driver.total_rides += 1
            
            if ride.passenger_id:
                passenger = self.db.query(User).filter(User.id == ride.passenger_id).first()
                if passenger:
                    passenger.total_rides += 1
            
            self.db.commit()
            self.db.refresh(ride)
            
            logger.info(f"Поездка {ride_id} завершена водителем {driver_id}")
            return ride
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка завершения поездки {ride_id}: {e}")
            raise

    def get_user_rides(self, user_id: int, role: str = "all") -> List[Ride]:
        """Получение поездок пользователя"""
        try:
            query = self.db.query(Ride)
            
            if role == "driver":
                query = query.filter(Ride.driver_id == user_id)
            elif role == "passenger":
                query = query.filter(Ride.passenger_id == user_id)
            else:
                query = query.filter(
                    or_(Ride.driver_id == user_id, Ride.passenger_id == user_id)
                )
            
            rides = query.order_by(desc(Ride.created_at)).all()
            return rides
            
        except Exception as e:
            logger.error(f"Ошибка получения поездок пользователя {user_id}: {e}")
            raise

    def update_ride(self, ride_id: int, ride_data: RideUpdate, driver_id: int) -> Ride:
        """Обновление поездки"""
        try:
            ride = self.get_ride(ride_id)
            if not ride:
                raise ValueError("Поездка не найдена")
            
            if ride.driver_id != driver_id:
                raise ValueError("Только водитель может изменить поездку")
            
            if ride.status != "active":
                raise ValueError("Нельзя изменить забронированную или завершенную поездку")
            
            # Обновление полей
            update_data = ride_data.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(ride, field):
                    setattr(ride, field, value)
            
            ride.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(ride)
            
            logger.info(f"Поездка {ride_id} обновлена водителем {driver_id}")
            return ride
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка обновления поездки {ride_id}: {e}")
            raise

    def get_ride_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики поездок пользователя"""
        try:
            # Поездки как водитель
            driver_rides = self.db.query(Ride).filter(Ride.driver_id == user_id).all()
            
            # Поездки как пассажир
            passenger_rides = self.db.query(Ride).filter(Ride.passenger_id == user_id).all()
            
            stats = {
                "total_as_driver": len(driver_rides),
                "total_as_passenger": len(passenger_rides),
                "completed_as_driver": len([r for r in driver_rides if r.status == "completed"]),
                "completed_as_passenger": len([r for r in passenger_rides if r.status == "completed"]),
                "cancelled_as_driver": len([r for r in driver_rides if r.status == "cancelled"]),
                "cancelled_as_passenger": len([r for r in passenger_rides if r.status == "cancelled"]),
                "total_earnings": sum([r.price for r in driver_rides if r.status == "completed"]),
                "total_spent": sum([r.price for r in passenger_rides if r.status == "completed"])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики пользователя {user_id}: {e}")
            raise

    def cleanup_expired_rides(self) -> int:
        """Очистка просроченных поездок"""
        try:
            expired_rides = self.db.query(Ride).filter(
                and_(
                    Ride.date < datetime.utcnow(),
                    Ride.status.in_(["active", "booked"])
                )
            ).all()
            
            count = 0
            for ride in expired_rides:
                ride.status = "expired"
                ride.updated_at = datetime.utcnow()
                count += 1
            
            self.db.commit()
            logger.info(f"Очищено {count} просроченных поездок")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка очистки просроченных поездок: {e}")
            raise

# Создание экземпляра сервиса
ride_service = RideService()