from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from ..utils.localization import get_error_message, get_success_message, get_general_message

class BaseResponse(BaseModel):
    """Базовая схема ответа"""
    success: bool = Field(..., description="Успешность операции")
    message: str = Field(..., description="Сообщение")
    request_id: str = Field(..., description="Уникальный ID запроса")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Временная метка")
    language: str = Field(default="ru", description="Язык ответа")

class SuccessResponse(BaseResponse):
    """Схема успешного ответа"""
    success: bool = Field(True, description="Успешность операции")
    data: Optional[Dict[str, Any]] = Field(None, description="Данные ответа")

class ErrorResponse(BaseResponse):
    """Схема ответа с ошибкой"""
    success: bool = Field(False, description="Успешность операции")
    error_code: str = Field(..., description="Код ошибки")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки")

class ValidationErrorResponse(BaseResponse):
    """Схема ответа с ошибкой валидации"""
    success: bool = Field(False, description="Успешность операции")
    error_code: str = Field("VALIDATION_ERROR", description="Код ошибки")
    field_errors: Dict[str, List[str]] = Field(..., description="Ошибки по полям")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки")

class AuthErrorResponse(BaseResponse):
    """Схема ответа с ошибкой аутентификации"""
    success: bool = Field(False, description="Успешность операции")
    error_code: str = Field("AUTH_ERROR", description="Код ошибки")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки")

class NotFoundErrorResponse(BaseResponse):
    """Схема ответа с ошибкой 'не найдено'"""
    success: bool = Field(False, description="Успешность операции")
    error_code: str = Field("NOT_FOUND", description="Код ошибки")
    resource_type: str = Field(..., description="Тип ресурса")
    resource_id: Optional[str] = Field(None, description="ID ресурса")

class PermissionErrorResponse(BaseResponse):
    """Схема ответа с ошибкой прав доступа"""
    success: bool = Field(False, description="Успешность операции")
    error_code: str = Field("PERMISSION_ERROR", description="Код ошибки")
    required_permissions: Optional[List[str]] = Field(None, description="Требуемые права")

class RateLimitErrorResponse(BaseResponse):
    """Схема ответа с ошибкой превышения лимита запросов"""
    success: bool = Field(False, description="Успешность операции")
    error_code: str = Field("RATE_LIMIT_ERROR", description="Код ошибки")
    retry_after: Optional[int] = Field(None, description="Время до следующей попытки в секундах")

class ServerErrorResponse(BaseResponse):
    """Схема ответа с серверной ошибкой"""
    success: bool = Field(False, description="Успешность операции")
    error_code: str = Field("SERVER_ERROR", description="Код ошибки")
    error_details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки")

class PaginatedResponse(BaseResponse):
    """Схема пагинированного ответа"""
    success: bool = Field(True, description="Успешность операции")
    data: List[Dict[str, Any]] = Field(..., description="Данные")
    pagination: Dict[str, Any] = Field(..., description="Информация о пагинации")

# Функции для создания ответов с локализацией
def create_success_response(
    data: Optional[Dict[str, Any]] = None,
    message_key: str = None,
    language: str = "ru",
    request_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание успешного ответа с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    if message_key:
        message = get_success_message(message_key, language, **kwargs)
    else:
        message = get_general_message("operation_successful", language)
    
    return {
        "success": True,
        "message": message,
        "data": data,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_error_response(
    error_code: str,
    message_key: str = None,
    language: str = "ru",
    request_id: str = None,
    error_details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание ответа с ошибкой с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    if message_key:
        message = get_error_message(message_key, language, **kwargs)
    else:
        message = get_error_message(error_code, language, **kwargs)
    
    return {
        "success": False,
        "message": message,
        "error_code": error_code,
        "error_details": error_details,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_validation_error_response(
    field_errors: Dict[str, List[str]],
    message_key: str = "validation.title",
    language: str = "ru",
    request_id: str = None,
    error_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Создание ответа с ошибкой валидации с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    message = get_error_message(message_key, language)
    
    return {
        "success": False,
        "message": message,
        "error_code": "VALIDATION_ERROR",
        "field_errors": field_errors,
        "error_details": error_details,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_auth_error_response(
    auth_error_code: str,
    message_key: str = None,
    language: str = "ru",
    request_id: str = None,
    error_details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание ответа с ошибкой аутентификации с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    if message_key:
        message = get_error_message(message_key, language, **kwargs)
    else:
        message = get_error_message(f"authentication.{auth_error_code}", language, **kwargs)
    
    return {
        "success": False,
        "message": message,
        "error_code": "AUTH_ERROR",
        "auth_error_code": auth_error_code,
        "error_details": error_details,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_not_found_error_response(
    resource_type: str,
    resource_id: Optional[str] = None,
    message_key: str = None,
    language: str = "ru",
    request_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание ответа с ошибкой 'не найдено' с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    if message_key:
        message = get_error_message(message_key, language, **kwargs)
    else:
        message = get_error_message(f"not_found.{resource_type}_not_found", language, **kwargs)
    
    return {
        "success": False,
        "message": message,
        "error_code": "NOT_FOUND",
        "resource_type": resource_type,
        "resource_id": resource_id,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_permission_error_response(
    required_permissions: Optional[List[str]] = None,
    message_key: str = "authorization.insufficient_permissions",
    language: str = "ru",
    request_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание ответа с ошибкой прав доступа с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    message = get_error_message(message_key, language, **kwargs)
    
    return {
        "success": False,
        "message": message,
        "error_code": "PERMISSION_ERROR",
        "required_permissions": required_permissions,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_rate_limit_error_response(
    retry_after: Optional[int] = None,
    message_key: str = "rate_limit.too_many_requests",
    language: str = "ru",
    request_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание ответа с ошибкой превышения лимита запросов с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    message = get_error_message(message_key, language, **kwargs)
    
    return {
        "success": False,
        "message": message,
        "error_code": "RATE_LIMIT_ERROR",
        "retry_after": retry_after,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_server_error_response(
    error_details: Optional[Dict[str, Any]] = None,
    message_key: str = "server.internal_error",
    language: str = "ru",
    request_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание ответа с серверной ошибкой с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    message = get_error_message(message_key, language, **kwargs)
    
    return {
        "success": False,
        "message": message,
        "error_code": "SERVER_ERROR",
        "error_details": error_details,
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    }

def create_paginated_response(
    data: List[Dict[str, Any]],
    page: int,
    limit: int,
    total: int,
    message_key: str = None,
    language: str = "ru",
    request_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """Создание пагинированного ответа с локализацией"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    if message_key:
        message = get_general_message(message_key, language, count=len(data), **kwargs)
    else:
        message = get_general_message("data_retrieved", language, count=len(data))
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "language": language
    } 