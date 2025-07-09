from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException, status

from ..models.ride import Ride
from ..models.user import User
from ..schemas.ride import RideCreate, RideUpdate, RideRead
from ..database import get_db

logger = logging.getLogger(__name__)

class RideService:
    def __init__(self):
        self.db: Session = next(get_db())

    def create_ride(self, ride_data: RideCreate, driver_id: int) -> Ride:
        """Создание новой поездки с оптимизированной валидацией"""
        try:
            # Оптимизированная проверка водителя - выбираем только необходимые поля
            driver = self.db.query(User.id, User.is_active, User.is_driver).filter(
                and_(User.id == driver_id, User.is_active == True)
            ).first()
            
            if not driver:
                raise ValueError("Водитель не найден или неактивен")
            
            if not driver.is_driver:
                raise ValueError("Пользователь не является водителем")
            
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
        """Получение поездки по ID с оптимизированным запросом"""
        try:
            # Используем joinedload для загрузки связанных данных одним запросом
            ride = self.db.query(Ride).options(
                joinedload(Ride.driver).load_only(User.id, User.full_name, User.average_rating, User.total_rides, User.avatar_url, User.phone),
                joinedload(Ride.passenger).load_only(User.id, User.full_name, User.average_rating, User.total_rides, User.avatar_url)
            ).filter(Ride.id == ride_id).first()
            
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
        """Оптимизированный поиск поездок с фильтрами"""
        try:
            # Базовый запрос с оптимизированной загрузкой связанных данных
            query = self.db.query(Ride).options(
                joinedload(Ride.driver).load_only(
                    User.id, User.full_name, User.average_rating, 
                    User.total_rides, User.avatar_url
                )
            ).filter(Ride.status == "active")
            
            # Применяем фильтры с оптимизацией
            if from_location:
                # Используем ILIKE для регистронезависимого поиска
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
            
            # Сортировка по дате (ближайшие сначала) с индексом
            query = query.order_by(asc(Ride.date))
            
            # Пагинация с ограничением
            rides = query.limit(limit).offset(offset).all()
            
            logger.info(f"Найдено {len(rides)} поездок с параметрами: from={from_location}, to={to_location}, date_from={date_from}, date_to={date_to}")
            return rides
            
        except Exception as e:
            logger.error(f"Ошибка поиска поездок: {e}")
            raise

    def book_ride(self, ride_id: int, passenger_id: int) -> Ride:
        """Бронирование поездки с оптимизированными запросами"""
        try:
            # Получение поездки с блокировкой для обновления
            ride = self.db.query(Ride).filter(Ride.id == ride_id).with_for_update().first()
            if not ride:
                raise ValueError("Поездка не найдена")
            
            # Проверка статуса
            if ride.status != "active":
                raise ValueError("Поездка недоступна для бронирования")
            
            # Проверка, что пассажир не является водителем
            if ride.driver_id == passenger_id:
                raise ValueError("Водитель не может забронировать свою поездку")
            
            # Оптимизированная проверка пассажира
            passenger = self.db.query(User.id, User.is_active).filter(
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
        """Отмена поездки с оптимизированными запросами"""
        try:
            # Получение поездки с блокировкой
            ride = self.db.query(Ride).filter(Ride.id == ride_id).with_for_update().first()
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
            
            logger.info(f"Поездка {ride_id} отменена пользователем {user_id} (водитель: {is_driver})")
            return ride
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка отмены поездки {ride_id}: {e}")
            raise

    def complete_ride(self, ride_id: int, driver_id: int) -> Ride:
        """Завершение поездки с оптимизированными запросами"""
        try:
            # Получение поездки с блокировкой
            ride = self.db.query(Ride).filter(Ride.id == ride_id).with_for_update().first()
            if not ride:
                raise ValueError("Поездка не найдена")
            
            # Проверка прав
            if ride.driver_id != driver_id:
                raise ValueError("Только водитель может завершить поездку")
            
            # Проверка статуса
            if ride.status not in ["booked", "active"]:
                raise ValueError("Поездка не может быть завершена")
            
            # Завершение
            ride.status = "completed"
            ride.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(ride)
            
            logger.info(f"Поездка {ride_id} завершена водителем {driver_id}")
            return ride
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка завершения поездки {ride_id}: {e}")
            raise

    def get_user_rides(self, user_id: int, role: str = "all") -> List[Ride]:
        """Получение поездок пользователя с оптимизированными запросами"""
        try:
            query = self.db.query(Ride).options(
                joinedload(Ride.driver).load_only(User.id, User.full_name, User.avatar_url),
                joinedload(Ride.passenger).load_only(User.id, User.full_name, User.avatar_url)
            )
            
            if role == "driver":
                query = query.filter(Ride.driver_id == user_id)
            elif role == "passenger":
                query = query.filter(Ride.passenger_id == user_id)
            else:  # all
                query = query.filter(
                    or_(Ride.driver_id == user_id, Ride.passenger_id == user_id)
                )
            
            rides = query.order_by(desc(Ride.created_at)).limit(100).all()
            
            logger.info(f"Получено {len(rides)} поездок для пользователя {user_id} (роль: {role})")
            return rides
            
        except Exception as e:
            logger.error(f"Ошибка получения поездок пользователя {user_id}: {e}")
            raise

    def update_ride(self, ride_id: int, ride_data: RideUpdate, driver_id: int) -> Ride:
        """Обновление поездки с оптимизированными запросами"""
        try:
            # Получение поездки с блокировкой
            ride = self.db.query(Ride).filter(Ride.id == ride_id).with_for_update().first()
            if not ride:
                raise ValueError("Поездка не найдена")
            
            # Проверка прав
            if ride.driver_id != driver_id:
                raise ValueError("Только водитель может изменить поездку")
            
            # Проверка возможности изменения
            if ride.status not in ["active", "booked"]:
                raise ValueError("Поездка не может быть изменена")
            
            # Обновление полей
            if ride_data.from_location is not None:
                ride.from_location = ride_data.from_location
            
            if ride_data.to_location is not None:
                ride.to_location = ride_data.to_location
            
            if ride_data.date is not None:
                if ride_data.date <= datetime.utcnow():
                    raise ValueError("Дата поездки должна быть в будущем")
                ride.date = ride_data.date
            
            if ride_data.price is not None:
                if ride_data.price <= 0:
                    raise ValueError("Цена должна быть больше 0")
                ride.price = ride_data.price
            
            if ride_data.seats is not None:
                if ride_data.seats <= 0 or ride_data.seats > 8:
                    raise ValueError("Количество мест должно быть от 1 до 8")
                ride.seats = ride_data.seats
            
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
        """Получение статистики поездок с оптимизированными запросами"""
        try:
            # Статистика как водителя
            driver_stats = self.db.query(
                func.count(Ride.id).label('total_rides'),
                func.sum(Ride.price).label('total_earnings'),
                func.avg(Ride.price).label('avg_price')
            ).filter(
                and_(Ride.driver_id == user_id, Ride.status == "completed")
            ).first()
            
            # Статистика как пассажира
            passenger_stats = self.db.query(
                func.count(Ride.id).label('total_rides'),
                func.sum(Ride.price).label('total_spent'),
                func.avg(Ride.price).label('avg_price')
            ).filter(
                and_(Ride.passenger_id == user_id, Ride.status == "completed")
            ).first()
            
            # Активные поездки
            active_rides = self.db.query(func.count(Ride.id)).filter(
                and_(
                    or_(Ride.driver_id == user_id, Ride.passenger_id == user_id),
                    Ride.status.in_(["active", "booked"])
                )
            ).scalar()
            
            statistics = {
                "driver": {
                    "total_rides": driver_stats.total_rides or 0,
                    "total_earnings": float(driver_stats.total_earnings or 0),
                    "avg_price": float(driver_stats.avg_price or 0)
                },
                "passenger": {
                    "total_rides": passenger_stats.total_rides or 0,
                    "total_spent": float(passenger_stats.total_spent or 0),
                    "avg_price": float(passenger_stats.avg_price or 0)
                },
                "active_rides": active_rides or 0
            }
            
            logger.info(f"Получена статистика для пользователя {user_id}")
            return statistics
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики пользователя {user_id}: {e}")
            raise

    def cleanup_expired_rides(self) -> int:
        """Очистка устаревших поездок с оптимизированными запросами"""
        try:
            # Находим поездки старше 30 дней
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Получаем количество удаляемых поездок
            count = self.db.query(func.count(Ride.id)).filter(
                and_(Ride.date < cutoff_date, Ride.status.in_(["cancelled", "completed"]))
            ).scalar()
            
            # Удаляем устаревшие поездки
            deleted = self.db.query(Ride).filter(
                and_(Ride.date < cutoff_date, Ride.status.in_(["cancelled", "completed"]))
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Удалено {deleted} устаревших поездок")
            return deleted
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка очистки устаревших поездок: {e}")
            raise

# Создаем экземпляр сервиса
ride_service = RideService()