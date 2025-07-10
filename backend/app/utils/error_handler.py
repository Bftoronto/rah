"""
Централизованный обработчик ошибок для устранения дублирования кода
"""
from typing import Callable, Any, Optional, TypeVar, Dict
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from datetime import datetime
from pydantic import BaseModel
from .logger import get_logger

logger = get_logger("error_handler")

T = TypeVar('T')

class ErrorResponse(BaseModel):
    """Стандартная схема ответа с ошибкой"""
    error: str
    detail: str
    timestamp: str
    code: Optional[str] = None
    user_id: Optional[int] = None
    request_id: Optional[str] = None

class APIErrorHandler:
    """Централизованная обработка ошибок API"""
    
    @staticmethod
    def handle_auth_error(error: Exception, user_id: Optional[int] = None) -> HTTPException:
        """Обработка ошибок авторизации"""
        logger.error(f"Ошибка авторизации: {str(error)}", extra={"user_id": user_id})
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации"
        )
    
    @staticmethod
    def handle_validation_error(error: Exception, field: Optional[str] = None) -> HTTPException:
        """Обработка ошибок валидации"""
        logger.error(f"Ошибка валидации: {str(error)}", extra={"field": field})
        detail = f"Ошибка валидации: {str(error)}"
        if field:
            detail = f"Ошибка валидации поля '{field}': {str(error)}"
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
    
    @staticmethod
    def handle_not_found_error(resource: str, resource_id: Optional[str] = None) -> HTTPException:
        """Обработка ошибок 'не найдено'"""
        detail = f"{resource} не найден"
        if resource_id:
            detail = f"{resource} с ID {resource_id} не найден"
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    @staticmethod
    def handle_permission_error(user_id: Optional[int] = None) -> HTTPException:
        """Обработка ошибок доступа"""
        logger.warning(f"Попытка несанкционированного доступа", extra={"user_id": user_id})
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    @staticmethod
    def handle_server_error(error: Exception, operation: str = "unknown") -> HTTPException:
        """Обработка серверных ошибок"""
        logger.error(f"Серверная ошибка в {operation}: {str(error)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )
    
    @staticmethod
    def handle_rate_limit_error() -> HTTPException:
        """Обработка ошибок ограничения запросов"""
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Превышен лимит запросов. Попробуйте позже."
        )

class ErrorHandler:
    """Централизованный обработчик ошибок"""
    
    @staticmethod
    def handle_database_operation(
        operation_name: str,
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Декоратор для обработки операций с базой данных"""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                try:
                    return func(*args, **kwargs)
                except IntegrityError as e:
                    logger.error(f"Ошибка целостности данных в {operation_name}: {str(e)}", 
                               extra={"user_id": user_id, "context": context})
                    if "telegram_id" in str(e).lower():
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Пользователь с таким Telegram ID уже существует"
                        )
                    elif "phone" in str(e).lower():
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Пользователь с таким номером телефона уже существует"
                        )
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Конфликт данных"
                        )
                except SQLAlchemyError as e:
                    logger.error(f"Ошибка базы данных в {operation_name}: {str(e)}", 
                               extra={"user_id": user_id, "context": context})
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Ошибка базы данных"
                    )
                except ValueError as e:
                    logger.warning(f"Ошибка валидации в {operation_name}: {str(e)}", 
                                 extra={"user_id": user_id, "context": context})
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e)
                    )
                except Exception as e:
                    logger.error(f"Неожиданная ошибка в {operation_name}: {str(e)}", 
                               exc_info=True, extra={"user_id": user_id, "context": context})
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Внутренняя ошибка сервера"
                    )
            return wrapper
        return decorator
    
    @staticmethod
    def handle_api_operation(
        operation_name: str,
        user_id: Optional[int] = None
    ):
        """Декоратор для обработки API операций"""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                try:
                    return func(*args, **kwargs)
                except HTTPException:
                    raise
                except ValueError as e:
                    logger.warning(f"Ошибка валидации в {operation_name}: {str(e)}", 
                                 extra={"user_id": user_id})
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e)
                    )
                except Exception as e:
                    logger.error(f"Неожиданная ошибка в {operation_name}: {str(e)}", 
                               exc_info=True, extra={"user_id": user_id})
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Внутренняя ошибка сервера"
                    )
            return wrapper
        return decorator

# Глобальные экземпляры для использования
error_handler = ErrorHandler()
api_error_handler = APIErrorHandler() 