from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Рейтинг от 1 до 5 звезд")
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к рейтингу")
    review: Optional[str] = Field(None, max_length=1000, description="Отзыв к рейтингу (алиас для comment)")

    @root_validator(pre=False)
    def sync_comment_review(cls, values):
        """Синхронизируем comment и review поля для совместимости"""
        comment = values.get('comment')
        review = values.get('review')
        
        # Если есть comment, но нет review - копируем
        if comment and not review:
            values['review'] = comment
        # Если есть review, но нет comment - копируем
        elif review and not comment:
            values['comment'] = review
        # Если оба пустые - оставляем как есть
        
        return values

class RatingCreate(RatingBase):
    target_user_id: int = Field(..., description="ID пользователя, которого оценивают")
    ride_id: int = Field(..., description="ID поездки")

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Рейтинг должен быть от 1 до 5')
        return v
    
    @validator('comment')
    def validate_comment(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Комментарий должен содержать минимум 10 символов')
        return v.strip() if v else v
    
    @validator('review')
    def validate_review(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Отзыв должен содержать минимум 10 символов')
        return v.strip() if v else v

class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Рейтинг от 1 до 5 звезд")
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к рейтингу")
    review: Optional[str] = Field(None, max_length=1000, description="Отзыв к рейтингу (алиас для comment)")

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Рейтинг должен быть от 1 до 5')
        return v
    
    @root_validator(pre=False)
    def sync_comment_review(cls, values):
        """Синхронизируем comment и review поля для совместимости"""
        comment = values.get('comment')
        review = values.get('review')
        
        if comment and not review:
            values['review'] = comment
        elif review and not comment:
            values['comment'] = review
            
        return values

class RatingResponse(RatingBase):
    id: int
    from_user_id: int
    target_user_id: int
    ride_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @root_validator(pre=False)
    def ensure_comment_review_sync(cls, values):
        """Убеждаемся что comment и review синхронизированы в ответе"""
        comment = values.get('comment')
        review = values.get('review')
        
        if comment and not review:
            values['review'] = comment
        elif review and not comment:
            values['comment'] = review
            
        return values

# Алиас для обратной совместимости
RatingRead = RatingResponse

class ReviewBase(BaseModel):
    text: str = Field(..., min_length=10, max_length=2000, description="Текст отзыва")
    comment: Optional[str] = Field(None, description="Комментарий (алиас для text)")
    is_positive: bool = Field(..., description="Положительный или отрицательный отзыв")
    
    @root_validator(pre=False)
    def sync_text_comment(cls, values):
        """Синхронизируем text и comment поля"""
        text = values.get('text')
        comment = values.get('comment')
        
        if text and not comment:
            values['comment'] = text
        elif comment and not text:
            values['text'] = comment
            
        return values

class ReviewCreate(ReviewBase):
    target_user_id: int = Field(..., description="ID пользователя, о котором оставляют отзыв")
    ride_id: int = Field(..., description="ID поездки")

    @validator('text')
    def validate_text(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Текст отзыва должен содержать минимум 10 символов')
        return v.strip()
    
    @validator('is_positive')
    def validate_is_positive(cls, v):
        if not isinstance(v, bool):
            raise ValueError('is_positive должно быть булевым значением')
        return v

class ReviewResponse(ReviewBase):
    id: int
    from_user_id: int
    target_user_id: int
    ride_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserRatingSummary(BaseModel):
    total_ratings: int
    average_rating: float
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    positive_percentage: float
    recent_ratings: List[RatingResponse]
    recent_reviews: List[ReviewResponse]

class UserRatingsResponse(BaseModel):
    total_ratings: int
    average_rating: float
    rating_distribution: Dict[int, int]
    ratings: List[RatingResponse]
    page: int
    limit: int
    total_pages: int

class UserReviewsResponse(BaseModel):
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    positive_percentage: float
    reviews: List[ReviewResponse]
    page: int
    limit: int
    total_pages: int

class TopUserResponse(BaseModel):
    user_id: int
    full_name: str
    avatar_url: Optional[str]
    average_rating: float
    total_ratings: int

class RatingStatisticsResponse(BaseModel):
    total_ratings: int
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[int, int]
    daily_ratings: List[Dict[str, Any]]

class RideRatingsResponse(BaseModel):
    ratings: List[RatingResponse]
    total_ratings: int
    average_rating: float

# Стандартизированный формат ответа для всех rating endpoints
class StandardRatingResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None

class RatingCreateResponse(StandardRatingResponse):
    data: Optional[RatingResponse] = None

class ReviewCreateResponse(StandardRatingResponse):
    data: Optional[ReviewResponse] = None

class RatingListResponse(StandardRatingResponse):
    data: Optional[UserRatingsResponse] = None

class ReviewListResponse(StandardRatingResponse):
    data: Optional[UserReviewsResponse] = None
