import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.notification import NotificationLog, NotificationSettings
from ..config.settings import settings

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.session = None
    
    async def get_session(self):
        """Получение HTTP сессии"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Закрытие HTTP сессии"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def log_notification(self, db: Session, user_id: int, notification_type: str, 
                        title: Optional[str] = None, message: Optional[str] = None,
                        success: bool = False, error_message: Optional[str] = None,
                        telegram_response: Optional[Dict] = None):
        """Логирование уведомления в базу данных"""
        try:
            log_entry = NotificationLog(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                success=success,
                error_message=error_message,
                telegram_response=telegram_response
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Ошибка логирования уведомления: {str(e)}")
            db.rollback()
    
    def check_notification_settings(self, db: Session, user_id: int, 
                                  notification_type: str) -> bool:
        """Проверка настроек уведомлений пользователя"""
        try:
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.user_id == user_id
            ).first()
            
            if not settings:
                # Создаем настройки по умолчанию
                settings = NotificationSettings(user_id=user_id)
                db.add(settings)
                db.commit()
                return True
            
            # Проверяем тип уведомления
            if notification_type.startswith("ride_"):
                return settings.ride_notifications
            elif notification_type in ["info", "success", "warning", "error", "security"]:
                return settings.system_notifications
            elif notification_type == "reminder":
                return settings.reminder_notifications
            elif notification_type == "marketing":
                return settings.marketing_notifications
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки настроек уведомлений: {str(e)}")
            return True  # По умолчанию разрешаем
    
    def is_quiet_hours(self, db: Session, user_id: int) -> bool:
        """Проверка тихих часов"""
        try:
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.user_id == user_id
            ).first()
            
            if not settings or not settings.quiet_hours_start or not settings.quiet_hours_end:
                return False
            
            now = datetime.now().time()
            start_time = datetime.strptime(settings.quiet_hours_start, "%H:%M").time()
            end_time = datetime.strptime(settings.quiet_hours_end, "%H:%M").time()
            
            if start_time <= end_time:
                return start_time <= now <= end_time
            else:
                # Переход через полночь
                return now >= start_time or now <= end_time
                
        except Exception as e:
            logger.error(f"Ошибка проверки тихих часов: {str(e)}")
            return False
    
    async def send_telegram_message(self, chat_id: str, text: str, 
                                  parse_mode: str = "HTML", 
                                  reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        """Отправка сообщения в Telegram"""
        try:
            session = await self.get_session()
            
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            if reply_markup:
                payload["reply_markup"] = reply_markup
            
            async with session.post(f"{self.base_url}/sendMessage", json=payload) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("ok"):
                    logger.info(f"Уведомление отправлено пользователю {chat_id}")
                    return {
                        "success": True,
                        "response": result
                    }
                else:
                    logger.error(f"Ошибка Telegram API: {result}")
                    return {
                        "success": False,
                        "error": result.get("description", "Unknown error"),
                        "response": result
                    }
                    
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_ride_notification(self, user: User, ride_data: Dict, 
                                   notification_type: str, db: Session) -> bool:
        """Уведомления о поездках"""
        try:
            if not user.telegram_id:
                logger.warning(f"Пользователь {user.id} не имеет Telegram ID")
                self.log_notification(db, user.id, notification_type, 
                                   success=False, error_message="No Telegram ID")
                return False
            
            # Проверяем настройки уведомлений
            if not self.check_notification_settings(db, user.id, notification_type):
                logger.info(f"Уведомления отключены для пользователя {user.id}")
                return True  # Не считаем ошибкой
            
            # Проверяем тихие часы
            if self.is_quiet_hours(db, user.id):
                logger.info(f"Тихие часы для пользователя {user.id}")
                return True  # Не считаем ошибкой
            
            # Шаблоны уведомлений
            templates = {
                "new_ride": {
                    "title": "🚗 Новая поездка",
                    "text": f"""
<b>Новая поездка по вашему маршруту!</b>

📍 <b>Маршрут:</b> {ride_data.get('from', '')} → {ride_data.get('to', '')}
📅 <b>Дата:</b> {ride_data.get('date', '')}
🕐 <b>Время:</b> {ride_data.get('time', '')}
💰 <b>Цена:</b> {ride_data.get('price', '')} ₽
👤 <b>Водитель:</b> {ride_data.get('driver_name', '')}
⭐ <b>Рейтинг:</b> {ride_data.get('driver_rating', '0')}
                    """.strip(),
                    "button": {"text": "Посмотреть поездку", "callback_data": f"view_ride_{ride_data.get('id')}"}
                },
                "ride_reminder": {
                    "title": "⏰ Напоминание о поездке",
                    "text": f"""
<b>Напоминание о поездке</b>

📍 <b>Маршрут:</b> {ride_data.get('from', '')} → {ride_data.get('to', '')}
📅 <b>Дата:</b> {ride_data.get('date', '')}
🕐 <b>Время:</b> {ride_data.get('time', '')}
🚗 <b>Автомобиль:</b> {ride_data.get('car_info', '')}
👤 <b>Водитель:</b> {ride_data.get('driver_name', '')}
📱 <b>Телефон:</b> {ride_data.get('driver_phone', '')}
                    """.strip(),
                    "button": {"text": "Открыть чат", "callback_data": f"open_chat_{ride_data.get('id')}"}
                },
                "ride_cancelled": {
                    "title": "❌ Поездка отменена",
                    "text": f"""
<b>Поездка отменена</b>

📍 <b>Маршрут:</b> {ride_data.get('from', '')} → {ride_data.get('to', '')}
📅 <b>Дата:</b> {ride_data.get('date', '')}
🕐 <b>Время:</b> {ride_data.get('time', '')}
📝 <b>Причина:</b> {ride_data.get('reason', 'Не указана')}
                    """.strip(),
                    "button": {"text": "Найти другую поездку", "callback_data": "find_ride"}
                },
                "booking_confirmed": {
                    "title": "✅ Бронирование подтверждено",
                    "text": f"""
<b>Ваше место забронировано!</b>

📍 <b>Маршрут:</b> {ride_data.get('from', '')} → {ride_data.get('to', '')}
📅 <b>Дата:</b> {ride_data.get('date', '')}
🕐 <b>Время:</b> {ride_data.get('time', '')}
💰 <b>Цена:</b> {ride_data.get('price', '')} ₽
👤 <b>Водитель:</b> {ride_data.get('driver_name', '')}
                    """.strip(),
                    "button": {"text": "Открыть чат", "callback_data": f"open_chat_{ride_data.get('id')}"}
                },
                "new_passenger": {
                    "title": "👤 Новый пассажир",
                    "text": f"""
<b>Новый пассажир забронировал место</b>

📍 <b>Маршрут:</b> {ride_data.get('from', '')} → {ride_data.get('to', '')}
📅 <b>Дата:</b> {ride_data.get('date', '')}
🕐 <b>Время:</b> {ride_data.get('time', '')}
👤 <b>Пассажир:</b> {ride_data.get('passenger_name', '')}
📱 <b>Телефон:</b> {ride_data.get('passenger_phone', '')}
                    """.strip(),
                    "button": {"text": "Открыть чат", "callback_data": f"open_chat_{ride_data.get('id')}"}
                }
            }
            
            template = templates.get(notification_type)
            if not template:
                logger.error(f"Неизвестный тип уведомления: {notification_type}")
                self.log_notification(db, user.id, notification_type, 
                                   success=False, error_message=f"Unknown type: {notification_type}")
                return False
            
            # Формируем клавиатуру
            reply_markup = None
            if template.get("button"):
                reply_markup = {
                    "inline_keyboard": [[template["button"]]]
                }
            
            # Отправляем уведомление
            result = await self.send_telegram_message(
                chat_id=user.telegram_id,
                text=template["text"],
                reply_markup=reply_markup
            )
            
            # Логируем результат
            self.log_notification(
                db=db,
                user_id=user.id,
                notification_type=notification_type,
                title=template["title"],
                message=template["text"],
                success=result["success"],
                error_message=result.get("error"),
                telegram_response=result.get("response")
            )
            
            return result["success"]
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о поездке: {str(e)}")
            self.log_notification(db, user.id, notification_type, 
                               success=False, error_message=str(e))
            return False
    
    async def send_system_notification(self, user: User, title: str, 
                                     message: str, notification_type: str = "info",
                                     db: Session = None) -> bool:
        """Системные уведомления"""
        try:
            if not user.telegram_id:
                if db:
                    self.log_notification(db, user.id, notification_type, 
                                       success=False, error_message="No Telegram ID")
                return False
            
            # Проверяем настройки уведомлений
            if db and not self.check_notification_settings(db, user.id, notification_type):
                logger.info(f"Системные уведомления отключены для пользователя {user.id}")
                return True
            
            # Проверяем тихие часы
            if db and self.is_quiet_hours(db, user.id):
                logger.info(f"Тихие часы для пользователя {user.id}")
                return True
            
            # Иконки для разных типов уведомлений
            icons = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌",
                "security": "🔒"
            }
            
            icon = icons.get(notification_type, "ℹ️")
            
            text = f"""
<b>{icon} {title}</b>

{message}
            """.strip()
            
            result = await self.send_telegram_message(
                chat_id=user.telegram_id,
                text=text
            )
            
            # Логируем результат
            if db:
                self.log_notification(
                    db=db,
                    user_id=user.id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    success=result["success"],
                    error_message=result.get("error"),
                    telegram_response=result.get("response")
                )
            
            return result["success"]
            
        except Exception as e:
            logger.error(f"Ошибка отправки системного уведомления: {str(e)}")
            if db:
                self.log_notification(db, user.id, notification_type, 
                                   success=False, error_message=str(e))
            return False
    
    async def send_reminder_notifications(self, db: Session) -> None:
        """Отправка напоминаний о поездках"""
        try:
            # Получаем поездки через 1 час
            from ..models.ride import Ride, Booking
            from sqlalchemy import and_
            
            reminder_time = datetime.now() + timedelta(hours=1)
            
            # Находим поездки через час
            rides = db.query(Ride).filter(
                and_(
                    Ride.date == reminder_time.date(),
                    Ride.time == reminder_time.strftime("%H:%M"),
                    Ride.is_active == True
                )
            ).all()
            
            for ride in rides:
                # Уведомляем водителя
                if ride.driver:
                    await self.send_ride_notification(
                        user=ride.driver,
                        ride_data={
                            "id": ride.id,
                            "from": ride.from_location,
                            "to": ride.to_location,
                            "date": ride.date.strftime("%d.%m.%Y"),
                            "time": ride.time,
                            "car_info": f"{ride.driver.car_brand} {ride.driver.car_model}",
                            "driver_name": ride.driver.full_name,
                            "driver_phone": ride.driver.phone
                        },
                        notification_type="ride_reminder",
                        db=db
                    )
                
                # Уведомляем пассажиров
                bookings = db.query(Booking).filter(
                    and_(
                        Booking.ride_id == ride.id,
                        Booking.status == "confirmed"
                    )
                ).all()
                
                for booking in bookings:
                    await self.send_ride_notification(
                        user=booking.passenger,
                        ride_data={
                            "id": ride.id,
                            "from": ride.from_location,
                            "to": ride.to_location,
                            "date": ride.date.strftime("%d.%m.%Y"),
                            "time": ride.time,
                            "car_info": f"{ride.driver.car_brand} {ride.driver.car_model}",
                            "driver_name": ride.driver.full_name,
                            "driver_phone": ride.driver.phone
                        },
                        notification_type="ride_reminder",
                        db=db
                    )
            
            logger.info(f"Отправлено {len(rides)} напоминаний о поездках")
            
        except Exception as e:
            logger.error(f"Ошибка отправки напоминаний: {str(e)}")
    
    async def send_bulk_notification(self, users: List[User], title: str, 
                                   message: str, notification_type: str = "info",
                                   db: Session = None) -> Dict[str, int]:
        """Массовая рассылка уведомлений"""
        results = {"success": 0, "failed": 0}
        
        for user in users:
            try:
                success = await self.send_system_notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    db=db
                )
                
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Ошибка отправки массового уведомления пользователю {user.id}: {str(e)}")
                results["failed"] += 1
        
        logger.info(f"Массовая рассылка завершена: {results['success']} успешно, {results['failed']} неудачно")
        return results

# Создание глобального экземпляра сервиса
notification_service = NotificationService() 