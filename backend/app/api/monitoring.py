from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import json

from ..database import get_db
from ..utils.error_handler import api_error_handler
from ..utils.logger import get_logger
from ..schemas.monitoring import FrontendError

logger = get_logger("monitoring")
router = APIRouter()

# Хранилище метрик (в продакшене лучше использовать Redis или базу данных)
metrics_store = []
errors_store = []

@router.post("/metrics")
async def receive_metrics(metrics_data: Dict[str, Any]):
    """Получение метрик производительности от фронтенда"""
    try:
        # Добавляем временную метку
        metrics_data["received_at"] = datetime.now().isoformat()
        
        # Сохраняем метрики
        metrics_store.append(metrics_data)
        
        # Ограничиваем количество хранимых метрик
        if len(metrics_store) > 1000:
            metrics_store.pop(0)
        
        # Логируем важные метрики
        if metrics_data.get("errorRate", 0) > 10:
            logger.warning(f"Высокий процент ошибок: {metrics_data.get('errorRate')}%")
        
        if metrics_data.get("avgResponseTime", 0) > 5000:
            logger.warning(f"Медленный ответ API: {metrics_data.get('avgResponseTime')}ms")
        
        return {"success": True, "message": "Метрики получены"}
        
    except Exception as e:
        logger.error(f"Ошибка обработки метрик: {str(e)}")
        raise api_error_handler.handle_server_error(e, "receive_metrics")

@router.post("/errors")
async def receive_errors(error_data: FrontendError):
    """Получение ошибок от фронтенда"""
    try:
        logger.error(f"Frontend error: {error_data.type} - {error_data.data.get('message', 'Unknown error')}")
        # Добавляем временную метку
        error_dict = error_data.dict()
        error_dict["received_at"] = datetime.now().isoformat()
        errors_store.append(error_dict)
        if len(errors_store) > 500:
            errors_store.pop(0)
        return {"success": True, "message": "Ошибка зарегистрирована"}
    except Exception as e:
        logger.error(f"Ошибка обработки ошибок: {str(e)}")
        raise api_error_handler.handle_server_error(e, "receive_errors")

@router.get("/stats")
async def get_monitoring_stats():
    """Получение статистики мониторинга"""
    try:
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        # Фильтруем метрики по времени
        recent_metrics = [
            m for m in metrics_store 
            if datetime.fromisoformat(m["received_at"]) > last_hour
        ]
        
        recent_errors = [
            e for e in errors_store 
            if datetime.fromisoformat(e["received_at"]) > last_hour
        ]
        
        # Вычисляем статистику
        total_sessions = len(set(m.get("sessionId") for m in recent_metrics))
        total_api_calls = sum(m.get("apiCalls", 0) for m in recent_metrics)
        total_errors = sum(m.get("errors", 0) for m in recent_metrics)
        
        avg_response_time = 0
        if recent_metrics:
            response_times = [m.get("avgResponseTime", 0) for m in recent_metrics]
            avg_response_time = sum(response_times) / len(response_times)
        
        avg_cache_hit_rate = 0
        if recent_metrics:
            hit_rates = [m.get("cacheHitRate", 0) for m in recent_metrics]
            avg_cache_hit_rate = sum(hit_rates) / len(hit_rates)
        
        # Статистика ошибок
        error_types = {}
        for error in recent_errors:
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "period": "last_hour",
            "total_sessions": total_sessions,
            "total_api_calls": total_api_calls,
            "total_errors": total_errors,
            "avg_response_time": round(avg_response_time, 2),
            "avg_cache_hit_rate": round(avg_cache_hit_rate, 2),
            "error_rate": round((total_errors / total_api_calls * 100) if total_api_calls > 0 else 0, 2),
            "error_types": error_types,
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {str(e)}")
        raise api_error_handler.handle_server_error(e, "get_monitoring_stats")

@router.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    try:
        # Проверяем доступность базы данных
        db_status = "healthy"
        try:
            # Здесь можно добавить проверку подключения к БД
            pass
        except Exception as e:
            db_status = "unhealthy"
            logger.error(f"Database health check failed: {str(e)}")
        
        # Проверяем память и ресурсы
        import psutil
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent()
        
        return {
            "status": "healthy" if db_status == "healthy" and memory_percent < 90 else "degraded",
            "database": db_status,
            "memory_usage": memory_percent,
            "cpu_usage": cpu_percent,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/alerts")
async def get_alerts():
    """Получение активных алертов"""
    try:
        alerts = []
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        
        # Проверяем метрики за последний час
        recent_metrics = [
            m for m in metrics_store 
            if datetime.fromisoformat(m["received_at"]) > last_hour
        ]
        
        # Алерт на высокий процент ошибок
        for metric in recent_metrics:
            if metric.get("errorRate", 0) > 10:
                alerts.append({
                    "type": "high_error_rate",
                    "severity": "warning",
                    "message": f"Высокий процент ошибок: {metric.get('errorRate')}%",
                    "session_id": metric.get("sessionId"),
                    "timestamp": metric.get("received_at")
                })
        
        # Алерт на медленные ответы
        for metric in recent_metrics:
            if metric.get("avgResponseTime", 0) > 5000:
                alerts.append({
                    "type": "slow_response",
                    "severity": "warning",
                    "message": f"Медленный ответ API: {metric.get('avgResponseTime')}ms",
                    "session_id": metric.get("sessionId"),
                    "timestamp": metric.get("received_at")
                })
        
        # Алерт на низкий hit rate кэша
        for metric in recent_metrics:
            if metric.get("cacheHitRate", 100) < 50:
                alerts.append({
                    "type": "low_cache_hit_rate",
                    "severity": "info",
                    "message": f"Низкий hit rate кэша: {metric.get('cacheHitRate')}%",
                    "session_id": metric.get("sessionId"),
                    "timestamp": metric.get("received_at")
                })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "timestamp": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения алертов: {str(e)}")
        raise api_error_handler.handle_server_error(e, "get_alerts")

@router.delete("/clear")
async def clear_monitoring_data():
    """Очистка данных мониторинга"""
    try:
        global metrics_store, errors_store
        metrics_store.clear()
        errors_store.clear()
        
        logger.info("Данные мониторинга очищены")
        return {"success": True, "message": "Данные мониторинга очищены"}
        
    except Exception as e:
        logger.error(f"Ошибка очистки данных мониторинга: {str(e)}")
        raise api_error_handler.handle_server_error(e, "clear_monitoring_data") 