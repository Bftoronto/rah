from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Рейтинг от 1 до 5 звезд")
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к рейтингу")

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

class RatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Рейтинг от 1 до 5 звезд")
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к рейтингу")

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Рейтинг должен быть от 1 до 5')
        return v

class RatingResponse(RatingBase):
    id: int
    from_user_id: int
    target_user_id: int
    ride_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Alias for backward compatibility
RatingRead = RatingResponse

class ReviewBase(BaseModel):
    text: str = Field(..., min_length=10, max_length=2000, description="Текст отзыва")
    is_positive: bool = Field(..., description="Положительный или отрицательный отзыв")

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