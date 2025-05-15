from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime, ForeignKey, Enum, event
from sqlalchemy.orm import declarative_base, relationship, Session
import enum
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

Base = declarative_base()

# Event listeners для логирования операций с базой данных
@event.listens_for(Session, 'after_commit')
def receive_after_commit(session):
    """Log after successful commit"""
    logger.info("Транзакция успешно завершена")

@event.listens_for(Session, 'after_rollback')
def receive_after_rollback(session):
    """Log after session rollback"""
    logger.error("Произошел откат транзакции")

@event.listens_for(Session, 'after_flush')
def receive_after_flush(session, flush_context):
    """Log newly created objects"""
    for instance in session.new:
        if isinstance(instance, Author):
            logger.info(f"Создан новый автор: {instance.display_name} (id: {instance.telegram_id})")
        elif isinstance(instance, Review):
            logger.info(f"Создан новый отзыв: категория '{instance.category}', объект '{instance.reference_name}'")
        elif isinstance(instance, Media):
            logger.info(f"Создан новый медиафайл: {instance.file_type} для отзыва #{instance.review_id}")

class ReviewCategory(enum.Enum):
    HOTEL = "отель"
    GUIDE = "гид"
    RESTAURANT = "ресторан"
    EXCURSION = "экскурсия"
    BEACH = "пляж"

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True)
    username = Column(String, nullable=True)
    display_name = Column(String, nullable=True, default='аноним')
    
    reviews = relationship("Review", back_populates="author")

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # Using String instead of Enum for flexibility
    reference_name = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    embedding = Column(Text, nullable=True)  # Using Text for now, can be changed to VECTOR or BYTEA
    
    author = relationship("Author", back_populates="reviews")
    media = relationship("Media", back_populates="review")

class Media(Base):
    __tablename__ = 'media'
    
    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, ForeignKey('reviews.id'), nullable=False)
    file_type = Column(String, nullable=False)  # photo, video, voice
    file_id = Column(Text, nullable=False)
    context_text = Column(Text, nullable=True)
    embedding = Column(Text, nullable=True)  # Using Text for now
    
    review = relationship("Review", back_populates="media")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)  # отели, гиды, рестораны, экскурсии, пляжи
    item_name = Column(Text, nullable=False)  # Конкретный объект

    @classmethod
    def get_items_by_category(cls, category_name: str) -> list[str]:
        """Возвращает список объектов для заданной категории"""
        ITEMS = {
            "отель": [
                "Arenas Doradas", "Barcelo Solymar", "Blau Varadero",
                # ... (полный список отелей)
            ],
            "гид": [
                "Александр. Гавана", "Вивьен. Гавана", "Галина. Варадеро",
                # ... (полный список гидов)
            ],
            "экскурсия": [
                "Авторские рассказы", "Дискавери тур. Джип сафари",
                # ... (полный список экскурсий)
            ],
            "ресторан": [
                "43.5 (43я улица)", "Bar Galeón (53я улица)", "Beatles Bar",
                # ... (полный список ресторанов)
            ],
            "пляж": [
                "пляж Arenas Doradas", "пляж Barcelo Solymar",
                # ... (полный список пляжей)
            ]
        }
        return ITEMS.get(category_name, []) 