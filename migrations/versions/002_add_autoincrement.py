"""Add autoincrement to authors.id

Revision ID: 002
Revises: 001
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создаем временную последовательность
    op.execute('CREATE SEQUENCE authors_id_seq')
    
    # Устанавливаем текущее значение последовательности
    op.execute('''
        SELECT setval('authors_id_seq', (SELECT MAX(id) FROM authors))
    ''')
    
    # Меняем колонку id на использование последовательности
    op.execute('''
        ALTER TABLE authors 
        ALTER COLUMN id 
        SET DEFAULT nextval('authors_id_seq')
    ''')

def downgrade() -> None:
    # Убираем значение по умолчанию
    op.execute('''
        ALTER TABLE authors 
        ALTER COLUMN id 
        DROP DEFAULT
    ''')
    
    # Удаляем последовательность
    op.execute('DROP SEQUENCE authors_id_seq') 