"""
Система метрик для мониторинга производительности
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Точка метрики"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Metric:
    """Метрика"""
    name: str
    description: str
    unit: str
    type: str  # counter, gauge, histogram
    points: deque = field(default_factory=lambda: deque(maxlen=1000))

class MetricsCollector:
    """Сборщик метрик"""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {}
        self.lock = threading.Lock()
        self._start_system_metrics()
    
    def register_metric(self, name: str, description: str, unit: str, metric_type: str = "gauge"):
        """Регистрация новой метрики"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = Metric(
                    name=name,
                    description=description,
                    unit=unit,
                    type=metric_type
                )
                logger.info(f"Зарегистрирована метрика: {name}")
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Запись значения метрики"""
        if name not in self.metrics:
            self.register_metric(name, f"Metric {name}", "count")
        
        with self.lock:
            metric = self.metrics[name]
            point = MetricPoint(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {}
            )
            metric.points.append(point)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Увеличение счетчика"""
        self.record_metric(name, value, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Установка значения gauge"""
        self.record_metric(name, value, labels)
    
    def record_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Запись в гистограмму"""
        self.record_metric(name, value, labels)
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Получение метрики по имени"""
        return self.metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, Metric]:
        """Получение всех метрик"""
        with self.lock:
            return self.metrics.copy()
    
    def get_metric_summary(self, name: str, window_minutes: int = 5) -> Dict[str, Any]:
        """Получение сводки метрики за период"""
        metric = self.get_metric(name)
        if not metric:
            return {}
        
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        recent_points = [
            point for point in metric.points 
            if point.timestamp >= window_start
        ]
        
        if not recent_points:
            return {"count": 0, "min": 0, "max": 0, "avg": 0}
        
        values = [point.value for point in recent_points]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else 0
        }
    
    def _start_system_metrics(self):
        """Запуск сбора системных метрик"""
        self.register_metric("system_cpu_percent", "CPU usage percentage", "percent")
        self.register_metric("system_memory_percent", "Memory usage percentage", "percent")
        self.register_metric("system_disk_usage", "Disk usage percentage", "percent")
        
        def collect_system_metrics():
            while True:
                try:
                    # CPU
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.set_gauge("system_cpu_percent", cpu_percent)
                    
                    # Memory
                    memory = psutil.virtual_memory()
                    self.set_gauge("system_memory_percent", memory.percent)
                    
                    # Disk
                    disk = psutil.disk_usage('/')
                    self.set_gauge("system_disk_usage", disk.percent)
                    
                    time.sleep(60)  # Обновление каждую минуту
                except Exception as e:
                    logger.error(f"Ошибка сбора системных метрик: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()

class APIMetrics:
    """Метрики API"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self._register_api_metrics()
    
    def _register_api_metrics(self):
        """Регистрация метрик API"""
        self.collector.register_metric("api_requests_total", "Total API requests", "count", "counter")
        self.collector.register_metric("api_requests_duration", "API request duration", "seconds", "histogram")
        self.collector.register_metric("api_requests_by_status", "API requests by status code", "count", "counter")
        self.collector.register_metric("api_requests_by_endpoint", "API requests by endpoint", "count", "counter")
        self.collector.register_metric("api_errors_total", "Total API errors", "count", "counter")
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Запись метрики запроса"""
        # Общее количество запросов
        self.collector.increment_counter("api_requests_total")
        
        # Длительность запроса
        self.collector.record_histogram("api_requests_duration", duration)
        
        # Запросы по статус коду
        self.collector.increment_counter(
            "api_requests_by_status", 
            labels={"status_code": str(status_code)}
        )
        
        # Запросы по endpoint
        self.collector.increment_counter(
            "api_requests_by_endpoint",
            labels={"method": method, "path": path}
        )
        
        # Ошибки
        if status_code >= 400:
            self.collector.increment_counter("api_errors_total")

class DatabaseMetrics:
    """Метрики базы данных"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self._register_db_metrics()
    
    def _register_db_metrics(self):
        """Регистрация метрик БД"""
        self.collector.register_metric("db_queries_total", "Total database queries", "count", "counter")
        self.collector.register_metric("db_query_duration", "Database query duration", "seconds", "histogram")
        self.collector.register_metric("db_connections_active", "Active database connections", "count", "gauge")
        self.collector.register_metric("db_errors_total", "Total database errors", "count", "counter")
    
    def record_query(self, query_type: str, duration: float, success: bool = True):
        """Запись метрики запроса к БД"""
        self.collector.increment_counter("db_queries_total")
        self.collector.record_histogram("db_query_duration", duration)
        
        if not success:
            self.collector.increment_counter("db_errors_total")
    
    def set_connections(self, count: int):
        """Установка количества активных соединений"""
        self.collector.set_gauge("db_connections_active", count)

# Глобальный экземпляр сборщика метрик
metrics_collector = MetricsCollector()
api_metrics = APIMetrics(metrics_collector)
db_metrics = DatabaseMetrics(metrics_collector) 