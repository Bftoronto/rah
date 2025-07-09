import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.rating import Rating, Review
from app.models.user import User
from app.models.ride import Ride
from app.schemas.rating import RatingCreate, ReviewCreate, RatingUpdate
from app.utils.security import get_current_user_id

logger = logging.getLogger(__name__)

class RatingService:
    def __init__(self, db: Session):
        self.db = db

    def create_rating(self, rating_data: RatingCreate, user_id: int) -> Rating:
        """Создание нового рейтинга"""
        try:
            # Проверяем, что пользователь не оценивает сам себя
            if rating_data.target_user_id == user_id:
                raise ValueError("Нельзя оценить самого себя")

            # Проверяем, что поездка существует и пользователь участвовал в ней
            ride = self.db.query(Ride).filter(Ride.id == rating_data.ride_id).first()
            if not ride:
                raise ValueError("Поездка не найдена")

            # Проверяем, что пользователь участвовал в поездке
            if ride.driver_id != user_id and ride.passenger_id != user_id:
                raise ValueError("Вы не участвовали в этой поездке")

            # Проверяем, что поездка завершена
            if ride.status != "completed":
                raise ValueError("Можно оценивать только завершенные поездки")

            # Проверяем, что рейтинг еще не был поставлен
            existing_rating = self.db.query(Rating).filter(
                and_(
                    Rating.ride_id == rating_data.ride_id,
                    Rating.from_user_id == user_id,
                    Rating.target_user_id == rating_data.target_user_id
                )
            ).first()

            if existing_rating:
                raise ValueError("Вы уже оценили этого пользователя за эту поездку")

            # Создаем рейтинг
            rating = Rating(
                from_user_id=user_id,
                target_user_id=rating_data.target_user_id,
                ride_id=rating_data.ride_id,
                rating=rating_data.rating,
                comment=rating_data.comment
            )

            self.db.add(rating)
            self.db.commit()
            self.db.refresh(rating)

            # Обновляем средний рейтинг пользователя
            self._update_user_average_rating(rating_data.target_user_id)

            logger.info(f"Создан рейтинг {rating.id} от пользователя {user_id} к пользователю {rating_data.target_user_id}")
            return rating

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания рейтинга: {str(e)}")
            raise

    def create_review(self, review_data: ReviewCreate, user_id: int) -> Review:
        """Создание нового отзыва"""
        try:
            # Проверяем, что пользователь не отзывается о самом себе
            if review_data.target_user_id == user_id:
                raise ValueError("Нельзя оставить отзыв о самом себе")

            # Проверяем, что отзыв еще не был оставлен
            existing_review = self.db.query(Review).filter(
                and_(
                    Review.ride_id == review_data.ride_id,
                    Review.from_user_id == user_id,
                    Review.target_user_id == review_data.target_user_id
                )
            ).first()

            if existing_review:
                raise ValueError("Вы уже оставили отзыв об этом пользователе за эту поездку")

            # Создаем отзыв
            review = Review(
                from_user_id=user_id,
                target_user_id=review_data.target_user_id,
                ride_id=review_data.ride_id,
                text=review_data.text,
                is_positive=review_data.is_positive
            )

            self.db.add(review)
            self.db.commit()
            self.db.refresh(review)

            logger.info(f"Создан отзыв {review.id} от пользователя {user_id} к пользователю {review_data.target_user_id}")
            return review

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания отзыва: {str(e)}")
            raise

    def update_rating(self, rating_id: int, rating_data: RatingUpdate, user_id: int) -> Rating:
        """Обновление рейтинга"""
        try:
            rating = self.db.query(Rating).filter(
                and_(
                    Rating.id == rating_id,
                    Rating.from_user_id == user_id
                )
            ).first()

            if not rating:
                raise ValueError("Рейтинг не найден или у вас нет прав на его редактирование")

            # Проверяем, что прошло не более 24 часов с момента создания
            if datetime.utcnow() - rating.created_at > timedelta(hours=24):
                raise ValueError("Рейтинг можно редактировать только в течение 24 часов")

            # Обновляем данные
            if rating_data.rating is not None:
                rating.rating = rating_data.rating
            if rating_data.comment is not None:
                rating.comment = rating_data.comment

            rating.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(rating)

            # Обновляем средний рейтинг пользователя
            self._update_user_average_rating(rating.target_user_id)

            logger.info(f"Обновлен рейтинг {rating_id} пользователем {user_id}")
            return rating

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка обновления рейтинга: {str(e)}")
            raise

    def delete_rating(self, rating_id: int, user_id: int) -> bool:
        """Удаление рейтинга"""
        try:
            rating = self.db.query(Rating).filter(
                and_(
                    Rating.id == rating_id,
                    Rating.from_user_id == user_id
                )
            ).first()

            if not rating:
                raise ValueError("Рейтинг не найден или у вас нет прав на его удаление")

            # Проверяем, что прошло не более 24 часов с момента создания
            if datetime.utcnow() - rating.created_at > timedelta(hours=24):
                raise ValueError("Рейтинг можно удалить только в течение 24 часов")

            target_user_id = rating.target_user_id
            self.db.delete(rating)
            self.db.commit()

            # Обновляем средний рейтинг пользователя
            self._update_user_average_rating(target_user_id)

            logger.info(f"Удален рейтинг {rating_id} пользователем {user_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка удаления рейтинга: {str(e)}")
            raise

    def get_user_ratings(self, user_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Получение рейтингов пользователя"""
        try:
            # Получаем общую статистику
            total_ratings = self.db.query(func.count(Rating.id)).filter(
                Rating.target_user_id == user_id
            ).scalar()

            avg_rating = self.db.query(func.avg(Rating.rating)).filter(
                Rating.target_user_id == user_id
            ).scalar() or 0.0

            # Получаем распределение по звездам
            rating_distribution = self.db.query(
                Rating.rating,
                func.count(Rating.id).label('count')
            ).filter(
                Rating.target_user_id == user_id
            ).group_by(Rating.rating).all()

            distribution = {i: 0 for i in range(1, 6)}
            for rating, count in rating_distribution:
                distribution[rating] = count

            # Получаем рейтинги с пагинацией
            offset = (page - 1) * limit
            ratings = self.db.query(Rating).filter(
                Rating.target_user_id == user_id
            ).order_by(Rating.created_at.desc()).offset(offset).limit(limit).all()

            return {
                "total_ratings": total_ratings,
                "average_rating": round(float(avg_rating), 2),
                "rating_distribution": distribution,
                "ratings": ratings,
                "page": page,
                "limit": limit,
                "total_pages": (total_ratings + limit - 1) // limit
            }

        except Exception as e:
            logger.error(f"Ошибка получения рейтингов пользователя: {str(e)}")
            raise

    def get_user_reviews(self, user_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Получение отзывов пользователя"""
        try:
            # Получаем общую статистику
            total_reviews = self.db.query(func.count(Review.id)).filter(
                Review.target_user_id == user_id
            ).scalar()

            positive_reviews = self.db.query(func.count(Review.id)).filter(
                and_(
                    Review.target_user_id == user_id,
                    Review.is_positive == True
                )
            ).scalar()

            # Получаем отзывы с пагинацией
            offset = (page - 1) * limit
            reviews = self.db.query(Review).filter(
                Review.target_user_id == user_id
            ).order_by(Review.created_at.desc()).offset(offset).limit(limit).all()

            return {
                "total_reviews": total_reviews,
                "positive_reviews": positive_reviews,
                "negative_reviews": total_reviews - positive_reviews,
                "positive_percentage": round((positive_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1),
                "reviews": reviews,
                "page": page,
                "limit": limit,
                "total_pages": (total_reviews + limit - 1) // limit
            }

        except Exception as e:
            logger.error(f"Ошибка получения отзывов пользователя: {str(e)}")
            raise

    def get_ride_ratings(self, ride_id: int) -> List[Rating]:
        """Получение рейтингов для конкретной поездки"""
        try:
            ratings = self.db.query(Rating).filter(
                Rating.ride_id == ride_id
            ).order_by(Rating.created_at.desc()).all()

            return ratings

        except Exception as e:
            logger.error(f"Ошибка получения рейтингов поездки: {str(e)}")
            raise

    def get_user_rating_summary(self, user_id: int) -> Dict[str, Any]:
        """Получение сводки рейтингов пользователя"""
        try:
            # Общая статистика рейтингов
            total_ratings = self.db.query(func.count(Rating.id)).filter(
                Rating.target_user_id == user_id
            ).scalar()

            avg_rating = self.db.query(func.avg(Rating.rating)).filter(
                Rating.target_user_id == user_id
            ).scalar() or 0.0

            # Статистика отзывов
            total_reviews = self.db.query(func.count(Review.id)).filter(
                Review.target_user_id == user_id
            ).scalar()

            positive_reviews = self.db.query(func.count(Review.id)).filter(
                and_(
                    Review.target_user_id == user_id,
                    Review.is_positive == True
                )
            ).scalar()

            # Последние рейтинги
            recent_ratings = self.db.query(Rating).filter(
                Rating.target_user_id == user_id
            ).order_by(Rating.created_at.desc()).limit(5).all()

            # Последние отзывы
            recent_reviews = self.db.query(Review).filter(
                Review.target_user_id == user_id
            ).order_by(Review.created_at.desc()).limit(5).all()

            return {
                "total_ratings": total_ratings,
                "average_rating": round(float(avg_rating), 2),
                "total_reviews": total_reviews,
                "positive_reviews": positive_reviews,
                "negative_reviews": total_reviews - positive_reviews,
                "positive_percentage": round((positive_reviews / total_reviews * 100) if total_reviews > 0 else 0, 1),
                "recent_ratings": recent_ratings,
                "recent_reviews": recent_reviews
            }

        except Exception as e:
            logger.error(f"Ошибка получения сводки рейтингов: {str(e)}")
            raise

    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение топ пользователей по рейтингу"""
        try:
            # Получаем пользователей с их средними рейтингами
            top_users = self.db.query(
                User.id,
                User.full_name,
                User.avatar_url,
                func.avg(Rating.rating).label('avg_rating'),
                func.count(Rating.id).label('total_ratings')
            ).join(Rating, User.id == Rating.target_user_id).group_by(
                User.id, User.full_name, User.avatar_url
            ).having(
                func.count(Rating.id) >= 3  # Минимум 3 оценки
            ).order_by(
                func.avg(Rating.rating).desc()
            ).limit(limit).all()

            return [
                {
                    "user_id": user.id,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "average_rating": round(float(user.avg_rating), 2),
                    "total_ratings": user.total_ratings
                }
                for user in top_users
            ]

        except Exception as e:
            logger.error(f"Ошибка получения топ пользователей: {str(e)}")
            raise

    def _update_user_average_rating(self, user_id: int) -> None:
        """Обновление среднего рейтинга пользователя"""
        try:
            avg_rating = self.db.query(func.avg(Rating.rating)).filter(
                Rating.target_user_id == user_id
            ).scalar() or 0.0

            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.average_rating = round(float(avg_rating), 2)
                self.db.commit()

        except Exception as e:
            logger.error(f"Ошибка обновления среднего рейтинга: {str(e)}")
            self.db.rollback()

    def get_rating_statistics(self) -> Dict[str, Any]:
        """Получение общей статистики рейтингов"""
        try:
            # Общая статистика
            total_ratings = self.db.query(func.count(Rating.id)).scalar()
            total_reviews = self.db.query(func.count(Review.id)).scalar()
            avg_rating = self.db.query(func.avg(Rating.rating)).scalar() or 0.0

            # Распределение по звездам
            rating_distribution = self.db.query(
                Rating.rating,
                func.count(Rating.id).label('count')
            ).group_by(Rating.rating).all()

            distribution = {i: 0 for i in range(1, 6)}
            for rating, count in rating_distribution:
                distribution[rating] = count

            # Статистика по дням (последние 30 дней)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            daily_ratings = self.db.query(
                func.date(Rating.created_at).label('date'),
                func.count(Rating.id).label('count')
            ).filter(
                Rating.created_at >= thirty_days_ago
            ).group_by(
                func.date(Rating.created_at)
            ).order_by(
                func.date(Rating.created_at)
            ).all()

            return {
                "total_ratings": total_ratings,
                "total_reviews": total_reviews,
                "average_rating": round(float(avg_rating), 2),
                "rating_distribution": distribution,
                "daily_ratings": [
                    {"date": str(day.date), "count": day.count}
                    for day in daily_ratings
                ]
            }

        except Exception as e:
            logger.error(f"Ошибка получения статистики рейтингов: {str(e)}")
            raise 