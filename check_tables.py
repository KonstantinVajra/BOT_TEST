from sqlalchemy import create_engine, inspect
import urllib.parse
from src.database import get_db
from src.models import Review, Media, Author, Category
from sqlalchemy import func

# Database connection parameters
params = {
    'host': '46.19.64.78',
    'port': '5432',
    'database': 'default_db',
    'user': 'gen_user',
    'password': ',Pw0VjKC\\Y\\2?P'
}

# Create database URL
url = f"postgresql://{params['user']}:{urllib.parse.quote_plus(params['password'])}@{params['host']}:{params['port']}/{params['database']}"

def main():
    db = next(get_db())
    
    # Проверяем все таблицы
    print("\nСтатистика базы данных:")
    print("-" * 30)
    
    # Категории
    categories = db.query(Category.name, func.count(Category.id))\
        .group_by(Category.name)\
        .all()
    print("\nКатегории:")
    for name, count in categories:
        print(f"{name}: {count} объектов")
    
    # Отзывы
    review_count = db.query(func.count(Review.id)).scalar()
    print(f"\nВсего отзывов: {review_count}")
    
    if review_count > 0:
        reviews_by_category = db.query(Review.category, func.count(Review.id))\
            .group_by(Review.category)\
            .all()
        print("\nОтзывы по категориям:")
        for category, count in reviews_by_category:
            print(f"{category}: {count} отзывов")
            
        # Показать последние 5 отзывов
        print("\nПоследние 5 отзывов:")
        latest_reviews = db.query(Review, Author)\
            .join(Author)\
            .order_by(Review.timestamp.desc())\
            .limit(5)\
            .all()
        
        for review, author in latest_reviews:
            print(f"\nКатегория: {review.category}")
            print(f"Объект: {review.reference_name}")
            print(f"Автор: {author.display_name}")
            print(f"Время: {review.timestamp}")
            print(f"Текст: {review.text if review.text else '[нет текста]'}")
    
    # Авторы
    author_count = db.query(func.count(Author.id)).scalar()
    print(f"\nВсего авторов: {author_count}")
    
    # Медиафайлы
    media_count = db.query(func.count(Media.id)).scalar()
    print(f"\nВсего медиафайлов: {media_count}")
    if media_count > 0:
        media_by_type = db.query(Media.file_type, func.count(Media.id))\
            .group_by(Media.file_type)\
            .all()
        print("\nМедиафайлы по типам:")
        for type_, count in media_by_type:
            print(f"{type_}: {count}")
    
    db.close()

if __name__ == "__main__":
    main()

try:
    # Create engine
    engine = create_engine(url)
    
    # Get inspector
    inspector = inspect(engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    print("\nСуществующие таблицы в базе данных:")
    for table in tables:
        print(f"\n{table}:")
        # Get columns for each table
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")
            
except Exception as e:
    print(f"Ошибка: {e}") 