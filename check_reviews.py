from src.database import get_db
from src.models import Review, Media, Author, Category
from sqlalchemy import func, text
import sys

def main():
    db = next(get_db())
    
    try:
        # Проверяем подключение к БД
        print("\nПроверка подключения к базе данных...")
        db.execute(text("SELECT 1")).scalar()
        print("✅ Подключение к базе данных успешно")
        
        # Проверяем таблицы
        print("\nПроверка таблиц:")
        
        # Categories
        cat_count = db.query(func.count(Category.id)).scalar()
        print(f"\nТаблица Categories: {cat_count} записей")
        if cat_count > 0:
            categories = db.query(Category.name, func.count(Category.id))\
                .group_by(Category.name)\
                .all()
            for name, count in categories:
                print(f"- {name}: {count} объектов")
        
        # Authors
        author_count = db.query(func.count(Author.id)).scalar()
        print(f"\nТаблица Authors: {author_count} записей")
        if author_count > 0:
            authors = db.query(Author).all()
            for author in authors:
                print(f"- {author.display_name} (id: {author.telegram_id})")
        
        # Reviews
        review_count = db.query(func.count(Review.id)).scalar()
        print(f"\nТаблица Reviews: {review_count} записей")
        if review_count > 0:
            reviews = db.query(Review.category, Review.reference_name, func.count(Review.id))\
                .group_by(Review.category, Review.reference_name)\
                .all()
            for category, ref_name, count in reviews:
                print(f"- {category} / {ref_name}: {count} отзывов")
            
            # Показываем последние 5 отзывов
            print("\nПоследние 5 отзывов:")
            latest = db.query(Review, Author)\
                .join(Author)\
                .order_by(Review.timestamp.desc())\
                .limit(5)\
                .all()
            
            for review, author in latest:
                print(f"\nОтзыв #{review.id}")
                print(f"Категория: {review.category}")
                print(f"Объект: {review.reference_name}")
                print(f"Автор: {author.display_name}")
                print(f"Время: {review.timestamp}")
                print(f"Текст: {review.text if review.text else '[нет текста]'}")
                
                # Проверяем медиафайлы для отзыва
                media = db.query(Media).filter(Media.review_id == review.id).all()
                if media:
                    print("Медиафайлы:")
                    for m in media:
                        print(f"- {m.file_type}: {m.file_id}")
        
        # Media
        media_count = db.query(func.count(Media.id)).scalar()
        print(f"\nТаблица Media: {media_count} записей")
        if media_count > 0:
            media_types = db.query(Media.file_type, func.count(Media.id))\
                .group_by(Media.file_type)\
                .all()
            for type_, count in media_types:
                print(f"- {type_}: {count} файлов")
                
    except Exception as e:
        print(f"\n❌ Ошибка при проверке базы данных: {str(e)}", file=sys.stderr)
    finally:
        db.close()

if __name__ == "__main__":
    main() 