from src.database import SessionLocal
from src.models import Review, Media
from sqlalchemy import func

db = SessionLocal()
try:
    # Получаем все уникальные названия отелей
    hotels = db.query(Review.reference_name)\
        .filter_by(category='отель')\
        .distinct()\
        .all()
    
    print('\nСписок отелей в базе:')
    for hotel in hotels:
        reviews = db.query(Review)\
            .filter_by(category='отель', reference_name=hotel[0])\
            .all()
        
        review_count = len(reviews)
        if review_count > 0:
            media_count = 0
            for review in reviews:
                media_count += db.query(Media).filter_by(review_id=review.id).count()
            
            print(f'\nОтель: {hotel[0]}')
            print(f'Отзывов: {review_count}')
            print(f'Медиафайлов: {media_count}')
            print('-' * 50)
finally:
    db.close() 