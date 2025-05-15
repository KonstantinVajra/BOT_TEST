from src.database import SessionLocal
from src.models import Author
from sqlalchemy import func

db = SessionLocal()
try:
    # Получаем всех авторов
    authors = db.query(Author).order_by(Author.id).all()
    
    print('\nСписок авторов:')
    print('-' * 50)
    for author in authors:
        print(f'ID: {author.id}')
        print(f'Telegram ID: {author.telegram_id}')
        print(f'Username: {author.username}')
        print(f'Display Name: {author.display_name}')
        print('-' * 50)
    
    # Статистика
    total = db.query(func.count(Author.id)).scalar()
    print(f'\nВсего авторов: {total}')
    
    # Проверяем максимальный ID
    max_id = db.query(func.max(Author.id)).scalar()
    print(f'Максимальный ID: {max_id}')
    
finally:
    db.close() 