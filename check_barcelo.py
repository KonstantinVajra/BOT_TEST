from src.database import SessionLocal
from src.models import Review, Media, Author
from sqlalchemy import func

db = SessionLocal()
try:
    # Подсчитываем отзывы
    reviews = db.query(Review, Author)\
        .join(Author)\
        .filter(Review.category == 'отель')\
        .filter(Review.reference_name == 'Barcelo Solymar')\
        .order_by(Review.timestamp)\
        .all()
    
    print(f'\nОтель Barcelo Solymar:')
    print(f'Количество отзывов: {len(reviews)}')
    
    # Показываем все отзывы
    print('\nВсе отзывы:')
    for review, author in reviews:
        media = db.query(Media).filter_by(review_id=review.id).all()
        print(f'\nДата: {review.timestamp}')
        print(f'Автор: {author.display_name}')
        print(f'Количество медиафайлов: {len(media)}')
        print('Типы медиафайлов:', ', '.join(m.file_type for m in media) if media else 'нет')
        print(f'Текст: {review.text}' if review.text else 'Текст: нет')
        print('-' * 50)
finally:
    db.close() 