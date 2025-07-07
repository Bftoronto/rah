from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from ..database import get_db
from ..services.moderation_service import moderation_service
from ..models.user import User
from ..models.ride import Ride
from ..schemas.moderation import (
    ReportCreate, ReportResponse, ActionCreate, ActionResponse,
    ContentCheckRequest, ContentCheckResponse, TrustScoreResponse,
    ModerationStatsResponse, RuleCreate, RuleResponse, FilterCreate,
    FilterResponse, UserViolationsResponse, BulkActionRequest
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/report", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    """Создание жалобы"""
    try:
        # Получаем текущего пользователя (в реальном приложении из токена)
        # Здесь используем заглушку для демонстрации
        current_user_id = 1  # В реальном приложении получаем из токена
        
        # Проверяем существование цели
        if report_data.target_type == "user":
            target = db.query(User).filter(User.id == report_data.target_id).first()
        elif report_data.target_type == "ride":
            target = db.query(Ride).filter(Ride.id == report_data.target_id).first()
        else:
            target = None
        
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Цель жалобы не найдена"
            )
        
        # Создаем жалобу
        report = moderation_service.create_report(
            db=db,
            reporter_id=current_user_id,
            target_type=report_data.target_type,
            target_id=report_data.target_id,
            reason=report_data.reason,
            description=report_data.description
        )
        
        return report.to_dict()
        
    except Exception as e:
        logger.error(f"Ошибка создания жалобы: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка создания жалобы"
        )

@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    status: str = None,
    target_type: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Получение списка жалоб"""
    try:
        reports = moderation_service.get_reports(
            db=db,
            status=status,
            target_type=target_type,
            limit=limit
        )
        
        return [report.to_dict() for report in reports]
        
    except Exception as e:
        logger.error(f"Ошибка получения жалоб: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения жалоб"
        )

@router.post("/reports/{report_id}/review", response_model=ActionResponse)
async def review_report(
    report_id: int,
    action_data: ActionCreate,
    db: Session = Depends(get_db)
):
    """Рассмотрение жалобы модератором"""
    try:
        # Получаем текущего модератора (в реальном приложении из токена)
        moderator_id = 1  # В реальном приложении получаем из токена
        
        # Рассматриваем жалобу
        action = moderation_service.review_report(
            db=db,
            report_id=report_id,
            moderator_id=moderator_id,
            action=action_data.action,
            reason=action_data.reason
        )
        
        return action.to_dict()
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка рассмотрения жалобы: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка рассмотрения жалобы"
        )

@router.post("/content/check", response_model=ContentCheckResponse)
async def check_content(
    check_data: ContentCheckRequest,
    db: Session = Depends(get_db)
):
    """Проверка контента на нарушения"""
    try:
        result = moderation_service.check_text_content(check_data.content)
        return result
        
    except Exception as e:
        logger.error(f"Ошибка проверки контента: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка проверки контента"
        )

@router.get("/users/{user_id}/trust-score", response_model=TrustScoreResponse)
async def get_user_trust_score(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получение доверия к пользователю"""
    try:
        trust_score = moderation_service.check_user_trust_score(db, user_id)
        return trust_score
        
    except Exception as e:
        logger.error(f"Ошибка получения доверия пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения доверия пользователя"
        )

@router.get("/users/{user_id}/violations", response_model=UserViolationsResponse)
async def get_user_violations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получение нарушений пользователя"""
    try:
        violations = moderation_service.get_user_violations(db, user_id)
        return violations
        
    except Exception as e:
        logger.error(f"Ошибка получения нарушений пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения нарушений пользователя"
        )

@router.get("/stats", response_model=ModerationStatsResponse)
async def get_moderation_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Получение статистики модерации"""
    try:
        stats = moderation_service.get_moderation_stats(db, days)
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики модерации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения статистики модерации"
        )

@router.post("/bulk-action")
async def bulk_action(
    action_data: BulkActionRequest,
    db: Session = Depends(get_db)
):
    """Массовые действия с жалобами"""
    try:
        # Получаем текущего модератора
        moderator_id = 1  # В реальном приложении получаем из токена
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        for report_id in action_data.report_ids:
            try:
                moderation_service.review_report(
                    db=db,
                    report_id=report_id,
                    moderator_id=moderator_id,
                    action=action_data.action,
                    reason=action_data.reason
                )
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "report_id": report_id,
                    "error": str(e)
                })
        
        return {
            "message": f"Обработано {results['success']} жалоб, ошибок: {results['failed']}",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка массовых действий: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка массовых действий"
        )

@router.post("/users/{user_id}/check-profile")
async def check_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Проверка профиля пользователя"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        result = moderation_service.check_user_profile(user)
        return result
        
    except Exception as e:
        logger.error(f"Ошибка проверки профиля пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка проверки профиля пользователя"
        )

@router.post("/rides/{ride_id}/check-content")
async def check_ride_content(
    ride_id: int,
    db: Session = Depends(get_db)
):
    """Проверка контента поездки"""
    try:
        ride = db.query(Ride).filter(Ride.id == ride_id).first()
        if not ride:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Поездка не найдена"
            )
        
        result = moderation_service.check_ride_content(ride)
        return result
        
    except Exception as e:
        logger.error(f"Ошибка проверки контента поездки: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка проверки контента поездки"
        )

@router.get("/auto-moderate")
async def auto_moderate_content(
    db: Session = Depends(get_db)
):
    """Автоматическая модерация контента"""
    try:
        # Получаем новые поездки для проверки
        new_rides = db.query(Ride).filter(
            and_(
                Ride.is_active == True,
                Ride.created_at >= datetime.now() - timedelta(hours=24)
            )
        ).all()
        
        results = {"checked": 0, "flagged": 0, "actions": []}
        
        for ride in new_rides:
            results["checked"] += 1
            check_result = moderation_service.check_ride_content(ride)
            
            if check_result["requires_review"]:
                results["flagged"] += 1
                results["actions"].append({
                    "ride_id": ride.id,
                    "score": check_result["score"],
                    "violations": check_result["violations"]
                })
        
        return {
            "message": f"Проверено {results['checked']} поездок, помечено {results['flagged']}",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Ошибка автоматической модерации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка автоматической модерации"
        ) 