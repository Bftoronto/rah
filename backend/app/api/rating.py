from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.rating_service import RatingService
from app.schemas.rating import (
    RatingCreate, RatingUpdate, RatingResponse, ReviewCreate, ReviewResponse,
    UserRatingSummary, UserRatingsResponse, UserReviewsResponse, TopUserResponse,
    RatingStatisticsResponse, RideRatingsResponse
)
from app.utils.security import get_current_user_id

router = APIRouter(prefix="/rating", tags=["rating"])

@router.post("/", response_model=RatingResponse)
@router.post("", response_model=RatingResponse)
def create_rating(
    rating_data: RatingCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание нового рейтинга"""
    try:
        rating_service = RatingService(db)
        rating = rating_service.create_rating(rating_data, current_user_id)
        return rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка создания рейтинга")

@router.post("/review", response_model=ReviewResponse)
@router.post("/review/", response_model=ReviewResponse)
def create_review(
    review_data: ReviewCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Создание нового отзыва"""
    try:
        rating_service = RatingService(db)
        review = rating_service.create_review(review_data, current_user_id)
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка создания отзыва")

@router.put("/{rating_id}", response_model=RatingResponse)
@router.put("/{rating_id}/", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating_data: RatingUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Обновление рейтинга"""
    try:
        rating_service = RatingService(db)
        rating = rating_service.update_rating(rating_id, rating_data, current_user_id)
        return rating
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка обновления рейтинга")

@router.delete("/{rating_id}")
@router.delete("/{rating_id}/")
def delete_rating(
    rating_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Удаление рейтинга"""
    try:
        rating_service = RatingService(db)
        success = rating_service.delete_rating(rating_id, current_user_id)
        return {"message": "Рейтинг успешно удален"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка удаления рейтинга")

@router.get("/user/{user_id}", response_model=UserRatingsResponse)
@router.get("/user/{user_id}/", response_model=UserRatingsResponse)
def get_user_ratings(
    user_id: int,
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=50, description="Количество записей на странице"),
    db: Session = Depends(get_db)
):
    """Получение рейтингов пользователя"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_user_ratings(user_id, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения рейтингов")

@router.get("/user/{user_id}/reviews", response_model=UserReviewsResponse)
@router.get("/user/{user_id}/reviews/", response_model=UserReviewsResponse)
def get_user_reviews(
    user_id: int,
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=50, description="Количество записей на странице"),
    db: Session = Depends(get_db)
):
    """Получение отзывов пользователя"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_user_reviews(user_id, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения отзывов")

@router.get("/user/{user_id}/summary", response_model=UserRatingSummary)
@router.get("/user/{user_id}/summary/", response_model=UserRatingSummary)
def get_user_rating_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получение сводки рейтингов пользователя"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_user_rating_summary(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения сводки рейтингов")

@router.get("/ride/{ride_id}", response_model=RideRatingsResponse)
@router.get("/ride/{ride_id}/", response_model=RideRatingsResponse)
def get_ride_ratings(
    ride_id: int,
    db: Session = Depends(get_db)
):
    """Получение рейтингов для конкретной поездки"""
    try:
        rating_service = RatingService(db)
        ratings = rating_service.get_ride_ratings(ride_id)
        
        # Вычисляем статистику
        total_ratings = len(ratings)
        if total_ratings > 0:
            average_rating = sum(r.rating for r in ratings) / total_ratings
        else:
            average_rating = 0.0
            
        return {
            "ratings": ratings,
            "total_ratings": total_ratings,
            "average_rating": round(average_rating, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения рейтингов поездки")

@router.get("/top", response_model=List[TopUserResponse])
@router.get("/top/", response_model=List[TopUserResponse])
def get_top_users(
    limit: int = Query(10, ge=1, le=50, description="Количество пользователей"),
    db: Session = Depends(get_db)
):
    """Получение топ пользователей по рейтингу"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_top_users(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения топ пользователей")

@router.get("/statistics", response_model=RatingStatisticsResponse)
@router.get("/statistics/", response_model=RatingStatisticsResponse)
def get_rating_statistics(
    db: Session = Depends(get_db)
):
    """Получение общей статистики рейтингов"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_rating_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения статистики")

@router.get("/my/ratings", response_model=UserRatingsResponse)
@router.get("/my/ratings/", response_model=UserRatingsResponse)
def get_my_ratings(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=50, description="Количество записей на странице"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение рейтингов текущего пользователя"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_user_ratings(current_user_id, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения рейтингов")

@router.get("/my/reviews", response_model=UserReviewsResponse)
@router.get("/my/reviews/", response_model=UserReviewsResponse)
def get_my_reviews(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(10, ge=1, le=50, description="Количество записей на странице"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение отзывов о текущем пользователе"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_user_reviews(current_user_id, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения отзывов")

@router.get("/my/summary", response_model=UserRatingSummary)
@router.get("/my/summary/", response_model=UserRatingSummary)
def get_my_rating_summary(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Получение сводки рейтингов текущего пользователя"""
    try:
        rating_service = RatingService(db)
        return rating_service.get_user_rating_summary(current_user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка получения сводки рейтингов") 