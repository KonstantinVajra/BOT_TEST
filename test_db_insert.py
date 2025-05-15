from datetime import datetime
from src.models import Author, Review, Media, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import os
from dotenv import load_dotenv
import random

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

def test_database_insert():
    try:
        # Создаем подключение
        engine = create_engine(DATABASE_URL, echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        logger.info("Testing database connection and inserts...")
        
        try:
            # Генерируем уникальный telegram_id
            test_telegram_id = random.randint(10000000, 99999999)
            
            # 1. Создаем тестового автора
            author = session.query(Author).filter_by(telegram_id=test_telegram_id).first()
            if not author:
                author = Author(
                    telegram_id=test_telegram_id,
                    username=f"test_user_{test_telegram_id}",
                    display_name=f"Test User {test_telegram_id}"
                )
                session.add(author)
                session.flush()
                logger.info(f"Created new test author with ID: {author.id}")
            else:
                logger.info(f"Using existing author with ID: {author.id}")
            
            # 2. Создаем тестовый отзыв
            review = Review(
                text="Это тестовый отзыв " + str(datetime.now()),
                category="отель",
                reference_name="Test Hotel",
                author=author,
                timestamp=datetime.now()
            )
            session.add(review)
            session.flush()
            logger.info(f"Created test review with ID: {review.id}")
            
            # 3. Создаем тестовый медиафайл
            media = Media(
                review=review,
                file_type="photo",
                file_id=f"test_file_id_{datetime.now().timestamp()}",
                context_text="Test media description"
            )
            session.add(media)
            
            # Сохраняем все изменения
            session.commit()
            logger.info("Successfully committed all test data")
            
            # Проверяем что данные действительно сохранились
            saved_review = session.query(Review).filter_by(id=review.id).first()
            saved_media = session.query(Media).filter_by(review_id=review.id).first()
            
            logger.info("Verification of saved data:")
            logger.info(f"Author: {author.display_name} (ID: {author.id})")
            logger.info(f"Review: {saved_review.text[:30]}... (ID: {saved_review.id})")
            logger.info(f"Media: {saved_media.file_type} (ID: {saved_media.id})")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error during database operations: {str(e)}", exc_info=True)
            raise
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_database_insert() 