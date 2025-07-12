"""
Модуль для сбора метрик приложения
"""
import time
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

from typing import Dict, Any, Optional
from ..utils.logger import get_logger

logger = get_logger("metrics")

class MetricsCollector:
    """Сборщик метрик приложения"""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "start_time": time.time(),
            "memory_usage": 0.0,
            "cpu_usage": 0.0
        }
    
    def increment_request(self, success: bool = True):
        """Увеличить счетчик запросов"""
        self.metrics["requests_total"] += 1
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1
    
    def update_system_metrics(self):
        """Обновить системные метрики"""
        try:
            # Используем psutil если доступен, иначе альтернативный способ
            if PSUTIL_AVAILABLE and psutil:
                process = psutil.Process()
                self.metrics["memory_usage"] = process.memory_info().rss / 1024 / 1024  # МБ
                self.metrics["cpu_usage"] = process.cpu_percent()
            else:
                # Альтернативный способ без psutil
                try:
                    with open('/proc/self/status', 'r') as f:
                        for line in f:
                            if line.startswith('VmRSS:'):
                                memory_kb = int(line.split()[1])
                                self.metrics["memory_usage"] = memory_kb / 1024
                                break
                except:
                    self.metrics["memory_usage"] = 0.0
                self.metrics["cpu_usage"] = 0.0
        except Exception as e:
            logger.error(f"Ошибка обновления системных метрик: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Получить текущие метрики"""
        self.update_system_metrics()
        return self.metrics.copy()
    
    def get_uptime(self) -> float:
        """Получить время работы приложения"""
        return time.time() - self.metrics["start_time"]

class APIMetrics:
    """Метрики API"""
    
    def __init__(self):
        self.endpoint_metrics = {}
        self.response_times = []
    
    def record_request(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """Записать метрику запроса"""
        key = f"{method}_{endpoint}"
        
        if key not in self.endpoint_metrics:
            self.endpoint_metrics[key] = {
                "count": 0,
                "success_count": 0,
                "error_count": 0,
                "total_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "avg_time": 0.0
            }
        
        metric = self.endpoint_metrics[key]
        metric["count"] += 1
        metric["total_time"] += duration_ms
        
        if 200 <= status_code < 400:
            metric["success_count"] += 1
        else:
            metric["error_count"] += 1
        
        metric["min_time"] = min(metric["min_time"], duration_ms)
        metric["max_time"] = max(metric["max_time"], duration_ms)
        metric["avg_time"] = metric["total_time"] / metric["count"]
        
        # Сохраняем время ответа для статистики
        self.response_times.append(duration_ms)
        if len(self.response_times) > 1000:  # Ограничиваем историю
            self.response_times.pop(0)
    
    def get_endpoint_metrics(self) -> Dict[str, Any]:
        """Получить метрики по эндпоинтам"""
        return self.endpoint_metrics.copy()
    
    def get_response_time_stats(self) -> Dict[str, float]:
        """Получить статистику времени ответа"""
        if not self.response_times:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0}
        
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        return {
            "avg": sum(sorted_times) / n,
            "min": sorted_times[0],
            "max": sorted_times[-1],
            "p95": sorted_times[int(n * 0.95)] if n > 0 else 0.0
        }

# Глобальные экземпляры
metrics_collector = MetricsCollector()
api_metrics = APIMetrics() 