from src.database import SessionLocal
from src.models import Review, Author, Media
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    try:
        # Общая статистика
        total_reviews = db.query(Review).count()
        total_authors = db.query(Author).count()
        total_media = db.query(Media).count()
        
        print(f"\nОбщая статистика:")
        print(f"Всего отзывов: {total_reviews}")
        print(f"Всего авторов: {total_authors}")
        print(f"Всего медиафайлов: {total_media}")
        
        # Статистика по отелю
        hotel_reviews = db.query(Review).filter_by(
            category='отель',
            reference_name='Arenas Doradas'
        ).all()
        
        print(f"\nСтатистика по отелю Arenas Doradas:")
        print(f"Количество отзывов: {len(hotel_reviews)}")
        print("\nСписок отзывов:")
        for review in hotel_reviews:
            media_count = db.query(Media).filter_by(review_id=review.id).count()
            author = db.query(Author).filter_by(id=review.author_id).first()
            print(f"\nID: {review.id}")
            print(f"Автор: {author.display_name}")
            print(f"Время: {review.timestamp}")
            print(f"Медиафайлов: {media_count}")
            print(f"Текст: {review.text[:100]}..." if review.text else "Текст: нет")
            print("-" * 50)
            
    finally:
        db.close()

if __name__ == "__main__":
    main() 