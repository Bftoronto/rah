import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from ..models.user import User
from ..models.ride import Ride
from ..models.moderation import ModerationReport, ModerationAction, ModerationRule
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ModerationService:
    def __init__(self):
        self.spam_patterns = [
            r'\b(купи|продам|заказать|звоните|телефон|вайбер|вацап)\b',
            r'\b(деньги|доллар|рубль|евро|кредит|займ)\b',
            r'\b(казино|ставки|играть|выигрыш)\b',
            r'\b(лекарства|таблетки|виагра|сиалис)\b',
            r'\b(порно|секс|интим|проститутка)\b',
            r'\b(взлом|хак|кража|мошенник)\b'
        ]
        
        self.toxic_patterns = [
            r'\b(идиот|дурак|кретин|дебил|тупой)\b',
            r'\b(сука|блять|хуй|пизда|ебать)\b',
            r'\b(нацист|фашист|расист|гомофоб)\b',
            r'\b(убить|сдохни|сдох|умри)\b'
        ]
        
        self.suspicious_patterns = [
            r'\b(бесплатно|даром|подарок|приз)\b',
            r'\b(быстро|срочно|немедленно|сейчас)\b',
            r'\b(гарантия|100%|точно|проверено)\b',
            r'\b(секрет|тайна|конфиденциально)\b'
        ]
        
        # Компилируем регулярные выражения для производительности
        self.spam_regex = re.compile('|'.join(self.spam_patterns), re.IGNORECASE)
        self.toxic_regex = re.compile('|'.join(self.toxic_patterns), re.IGNORECASE)
        self.suspicious_regex = re.compile('|'.join(self.suspicious_patterns), re.IGNORECASE)
    
    def check_text_content(self, text: str) -> Dict[str, Any]:
        """Проверка текстового контента на нарушения"""
        if not text:
            return {"clean": True, "score": 0, "violations": []}
        
        violations = []
        score = 0
        
        # Проверка на спам
        spam_matches = self.spam_regex.findall(text)
        if spam_matches:
            violations.append({
                "type": "spam",
                "severity": "high",
                "matches": spam_matches,
                "description": "Обнаружен спам-контент"
            })
            score += 50
        
        # Проверка на токсичность
        toxic_matches = self.toxic_regex.findall(text)
        if toxic_matches:
            violations.append({
                "type": "toxic",
                "severity": "medium",
                "matches": toxic_matches,
                "description": "Обнаружен токсичный контент"
            })
            score += 30
        
        # Проверка на подозрительный контент
        suspicious_matches = self.suspicious_regex.findall(text)
        if suspicious_matches:
            violations.append({
                "type": "suspicious",
                "severity": "low",
                "matches": suspicious_matches,
                "description": "Обнаружен подозрительный контент"
            })
            score += 10
        
        # Проверка на капс
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.7:
            violations.append({
                "type": "caps",
                "severity": "low",
                "ratio": caps_ratio,
                "description": "Слишком много заглавных букв"
            })
            score += 5
        
        # Проверка на повторяющиеся символы
        repeated_chars = re.findall(r'(.)\1{4,}', text)
        if repeated_chars:
            violations.append({
                "type": "repeated_chars",
                "severity": "low",
                "chars": repeated_chars,
                "description": "Повторяющиеся символы"
            })
            score += 5
        
        return {
            "clean": score < 20,
            "score": score,
            "violations": violations,
            "requires_review": score >= 30
        }
    
    def check_user_profile(self, user: User) -> Dict[str, Any]:
        """Проверка профиля пользователя"""
        violations = []
        score = 0
        
        # Проверка имени
        if user.full_name:
            name_check = self.check_text_content(user.full_name)
            if not name_check["clean"]:
                violations.extend(name_check["violations"])
                score += name_check["score"]
        
        # Проверка описания
        if user.about:
            about_check = self.check_text_content(user.about)
            if not about_check["clean"]:
                violations.extend(about_check["violations"])
                score += about_check["score"]
        
        # Проверка города
        if user.city:
            city_check = self.check_text_content(user.city)
            if not city_check["clean"]:
                violations.extend(city_check["violations"])
                score += city_check["score"]
        
        # Проверка возраста
        if user.birth_date:
            age = (datetime.now() - user.birth_date).days // 365
            if age < 18:
                violations.append({
                    "type": "underage",
                    "severity": "high",
                    "age": age,
                    "description": "Пользователь несовершеннолетний"
                })
                score += 100
        
        return {
            "clean": score < 20,
            "score": score,
            "violations": violations,
            "requires_review": score >= 30
        }
    
    def check_ride_content(self, ride: Ride) -> Dict[str, Any]:
        """Проверка контента поездки"""
        violations = []
        score = 0
        
        # Проверка маршрута
        if ride.from_location:
            from_check = self.check_text_content(ride.from_location)
            if not from_check["clean"]:
                violations.extend(from_check["violations"])
                score += from_check["score"]
        
        if ride.to_location:
            to_check = self.check_text_content(ride.to_location)
            if not to_check["clean"]:
                violations.extend(to_check["violations"])
                score += to_check["score"]
        
        # Проверка описания
        if ride.description:
            desc_check = self.check_text_content(ride.description)
            if not desc_check["clean"]:
                violations.extend(desc_check["violations"])
                score += desc_check["score"]
        
        # Проверка цены
        if ride.price and ride.price < 50:
            violations.append({
                "type": "suspicious_price",
                "severity": "medium",
                "price": ride.price,
                "description": "Подозрительно низкая цена"
            })
            score += 20
        
        if ride.price and ride.price > 10000:
            violations.append({
                "type": "suspicious_price",
                "severity": "medium",
                "price": ride.price,
                "description": "Подозрительно высокая цена"
            })
            score += 20
        
        return {
            "clean": score < 20,
            "score": score,
            "violations": violations,
            "requires_review": score >= 30
        }
    
    def create_report(self, db: Session, reporter_id: int, target_type: str, 
                     target_id: int, reason: str, description: str = None) -> ModerationReport:
        """Создание жалобы"""
        try:
            report = ModerationReport(
                reporter_id=reporter_id,
                target_type=target_type,
                target_id=target_id,
                reason=reason,
                description=description,
                status="pending"
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            logger.info(f"Создана жалоба {report.id} на {target_type} {target_id}")
            return report
            
        except Exception as e:
            logger.error(f"Ошибка создания жалобы: {str(e)}")
            db.rollback()
            raise
    
    def get_reports(self, db: Session, status: str = None, 
                   target_type: str = None, limit: int = 50) -> List[ModerationReport]:
        """Получение списка жалоб"""
        query = db.query(ModerationReport)
        
        if status:
            query = query.filter(ModerationReport.status == status)
        
        if target_type:
            query = query.filter(ModerationReport.target_type == target_type)
        
        return query.order_by(ModerationReport.created_at.desc()).limit(limit).all()
    
    def review_report(self, db: Session, report_id: int, moderator_id: int,
                     action: str, reason: str = None) -> ModerationAction:
        """Рассмотрение жалобы модератором"""
        try:
            report = db.query(ModerationReport).filter(ModerationReport.id == report_id).first()
            if not report:
                raise ValueError("Жалоба не найдена")
            
            # Создаем действие модератора
            moderation_action = ModerationAction(
                report_id=report_id,
                moderator_id=moderator_id,
                action=action,
                reason=reason
            )
            
            # Обновляем статус жалобы
            report.status = "resolved"
            report.resolved_at = datetime.now()
            
            # Применяем действие к цели
            self.apply_action(db, report.target_type, report.target_id, action)
            
            db.add(moderation_action)
            db.commit()
            db.refresh(moderation_action)
            
            logger.info(f"Жалоба {report_id} рассмотрена: {action}")
            return moderation_action
            
        except Exception as e:
            logger.error(f"Ошибка рассмотрения жалобы: {str(e)}")
            db.rollback()
            raise
    
    def apply_action(self, db: Session, target_type: str, target_id: int, action: str):
        """Применение действия модератора"""
        try:
            if target_type == "user":
                user = db.query(User).filter(User.id == target_id).first()
                if user:
                    if action == "warn":
                        user.warnings = (user.warnings or 0) + 1
                    elif action == "suspend":
                        user.is_suspended = True
                        user.suspended_until = datetime.now() + timedelta(days=7)
                    elif action == "ban":
                        user.is_banned = True
                        user.banned_at = datetime.now()
            
            elif target_type == "ride":
                ride = db.query(Ride).filter(Ride.id == target_id).first()
                if ride:
                    if action == "hide":
                        ride.is_hidden = True
                    elif action == "delete":
                        ride.is_active = False
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Ошибка применения действия {action}: {str(e)}")
            db.rollback()
            raise
    
    def get_user_violations(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Получение нарушений пользователя"""
        reports = db.query(ModerationReport).filter(
            and_(
                ModerationReport.target_type == "user",
                ModerationReport.target_id == user_id
            )
        ).all()
        
        actions = db.query(ModerationAction).join(ModerationReport).filter(
            ModerationReport.target_id == user_id
        ).all()
        
        return {
            "reports": [report.to_dict() for report in reports],
            "actions": [action.to_dict() for action in actions]
        }
    
    def check_user_trust_score(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Проверка доверия к пользователю"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"trust_score": 0, "level": "unknown"}
        
        # Базовый скор
        trust_score = 100
        
        # Штрафы за предупреждения
        if user.warnings:
            trust_score -= user.warnings * 20
        
        # Штрафы за жалобы
        reports = db.query(ModerationReport).filter(
            and_(
                ModerationReport.target_type == "user",
                ModerationReport.target_id == user_id,
                ModerationReport.status == "resolved"
            )
        ).count()
        trust_score -= reports * 15
        
        # Бонусы за возраст аккаунта
        if user.created_at:
            days_registered = (datetime.now() - user.created_at).days
            if days_registered > 30:
                trust_score += 10
            if days_registered > 90:
                trust_score += 20
        
        # Определение уровня доверия
        if trust_score >= 80:
            level = "high"
        elif trust_score >= 50:
            level = "medium"
        elif trust_score >= 20:
            level = "low"
        else:
            level = "suspicious"
        
        return {
            "trust_score": max(0, trust_score),
            "level": level,
            "warnings": user.warnings or 0,
            "reports": reports
        }
    
    def get_moderation_stats(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Получение статистики модерации"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Общее количество жалоб
        total_reports = db.query(ModerationReport).filter(
            ModerationReport.created_at >= start_date
        ).count()
        
        # Жалобы по статусам
        pending_reports = db.query(ModerationReport).filter(
            and_(
                ModerationReport.status == "pending",
                ModerationReport.created_at >= start_date
            )
        ).count()
        
        resolved_reports = db.query(ModerationReport).filter(
            and_(
                ModerationReport.status == "resolved",
                ModerationReport.created_at >= start_date
            )
        ).count()
        
        # Действия модераторов
        actions = db.query(ModerationAction).filter(
            ModerationAction.created_at >= start_date
        ).all()
        
        action_stats = {}
        for action in actions:
            action_stats[action.action] = action_stats.get(action.action, 0) + 1
        
        return {
            "period_days": days,
            "total_reports": total_reports,
            "pending_reports": pending_reports,
            "resolved_reports": resolved_reports,
            "action_stats": action_stats,
            "resolution_rate": (resolved_reports / total_reports * 100) if total_reports > 0 else 0
        }

# Создание глобального экземпляра сервиса
moderation_service = ModerationService() 