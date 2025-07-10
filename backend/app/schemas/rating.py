from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class RatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Рейтинг от 1 до 5 звезд")
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к рейтингу", alias="review")
    review: Optional[str] = Field(None, max_length=1000, description="Отзыв к рейтингу", alias="comment")

    @model_validator(mode='before')
    @classmethod
    def sync_comment_review(cls, values):
        """Синхронизация полей comment и review для совместимости"""
        if isinstance(values, dict):
            comment = values.get('comment')
            review = values.get('review')
            
            # Если указан только comment, копируем в review
            if comment and not review:
                values['review'] = comment
            # Если указан только review, копируем в comment
            elif review and not comment:
                values['comment'] = review
        
        return values

    class Config:
        populate_by_name = True
        validate_by_name = True

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
    comment: Optional[str] = Field(None, max_length=1000, description="Комментарий к рейтингу", alias="review")
    review: Optional[str] = Field(None, max_length=1000, description="Отзыв к рейтингу", alias="comment")

    @model_validator(mode='before')
    @classmethod
    def sync_comment_review(cls, values):
        """Синхронизация полей comment и review для совместимости"""
        if isinstance(values, dict):
            comment = values.get('comment')
            review = values.get('review')
            
            # Если указан только comment, копируем в review
            if comment and not review:
                values['review'] = comment
            # Если указан только review, копируем в comment
            elif review and not comment:
                values['comment'] = review
        
        return values

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
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

    class Config:
        populate_by_name = True
        validate_by_name = True

class RatingResponse(RatingBase):
    id: int
    from_user_id: int
    target_user_id: int
    ride_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        validate_by_name = True

# Alias for backward compatibility
RatingRead = RatingResponse

class ReviewBase(BaseModel):
    text: str = Field(..., min_length=10, max_length=2000, description="Текст отзыва")
    is_positive: bool = Field(..., description="Положительный или отрицательный отзыв")
    comment: Optional[str] = Field(None, max_length=1000, description="Дополнительный комментарий", alias="review")
    review: Optional[str] = Field(None, max_length=1000, description="Дополнительный отзыв", alias="comment")

    @model_validator(mode='before')
    @classmethod
    def sync_comment_review(cls, values):
        """Синхронизация полей comment и review для совместимости"""
        if isinstance(values, dict):
            comment = values.get('comment')
            review = values.get('review')
            
            # Если указан только comment, копируем в review
            if comment and not review:
                values['review'] = comment
            # Если указан только review, копируем в comment
            elif review and not comment:
                values['comment'] = review
        
        return values

    class Config:
        populate_by_name = True
        validate_by_name = True

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

class ReviewResponse(ReviewBase):
    id: int
    from_user_id: int
    target_user_id: int
    ride_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        validate_by_name = True

class UserRatingSummary(BaseModel):
    total_ratings: int
    average_rating: float
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    positive_percentage: float
    recent_ratings: List[RatingResponse]
    recent_reviews: List[ReviewResponse]

    class Config:
        populate_by_name = True
        validate_by_name = True

class UserRatingsResponse(BaseModel):
    total_ratings: int
    average_rating: float
    rating_distribution: Dict[int, int]
    ratings: List[RatingResponse]
    page: int
    limit: int
    total_pages: int

    class Config:
        populate_by_name = True
        validate_by_name = True

class UserReviewsResponse(BaseModel):
    total_reviews: int
    positive_reviews: int
    negative_reviews: int
    positive_percentage: float
    reviews: List[ReviewResponse]
    page: int
    limit: int
    total_pages: int

    class Config:
        populate_by_name = True
        validate_by_name = True

class TopUserResponse(BaseModel):
    user_id: int
    full_name: str
    avatar_url: Optional[str] = Field(None, alias="avatar")
    average_rating: float
    total_ratings: int

    class Config:
        from_attributes = True
        populate_by_name = True
        validate_by_name = True

class RatingStatisticsResponse(BaseModel):
    total_ratings: int
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[int, int]
    daily_ratings: List[Dict[str, Any]]

    class Config:
        populate_by_name = True
        validate_by_name = True

class RideRatingsResponse(BaseModel):
    ratings: List[RatingResponse]
    total_ratings: int
    average_rating: float

    class Config:
        populate_by_name = True
        validate_by_name = True 