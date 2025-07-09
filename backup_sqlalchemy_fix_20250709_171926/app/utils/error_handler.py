"""
Централизованный обработчик ошибок для устранения дублирования кода
"""
from typing import Callable, Any, Optional, TypeVar, Dict
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from .logger import get_logger

logger = get_logger("error_handler")

T = TypeVar('T')

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
                    logger.error(f"Ошибка целостности данных в {operation_name}: {str(e)}")
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
                    logger.error(f"Ошибка базы данных в {operation_name}: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Ошибка базы данных"
                    )
                except ValueError as e:
                    logger.warning(f"Ошибка валидации в {operation_name}: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e)
                    )
                except Exception as e:
                    logger.error(f"Неожиданная ошибка в {operation_name}: {str(e)}", exc_info=True)
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
                    logger.warning(f"Ошибка валидации в {operation_name}: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e)
                    )
                except Exception as e:
                    logger.error(f"Неожиданная ошибка в {operation_name}: {str(e)}", exc_info=True)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Внутренняя ошибка сервера"
                    )
            return wrapper
        return decorator

# Глобальный экземпляр для использования
error_handler = ErrorHandler() 