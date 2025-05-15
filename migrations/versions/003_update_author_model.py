"""Update Author model

Revision ID: 003
Revises: 002
Create Date: 2024-03-19 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создаем временную последовательность для id если её нет
    op.execute('CREATE SEQUENCE IF NOT EXISTS authors_id_seq')
    
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
    
    # Добавляем UNIQUE constraint для telegram_id
    op.create_unique_constraint('uq_authors_telegram_id', 'authors', ['telegram_id'])
    
    # Делаем telegram_id NOT NULL
    op.alter_column('authors', 'telegram_id',
                    existing_type=sa.BIGINT(),
                    nullable=False)

def downgrade() -> None:
    # Удаляем UNIQUE constraint для telegram_id
    op.drop_constraint('uq_authors_telegram_id', 'authors')
    
    # Делаем telegram_id nullable
    op.alter_column('authors', 'telegram_id',
                    existing_type=sa.BIGINT(),
                    nullable=True)
    
    # Убираем значение по умолчанию для id
    op.execute('''
        ALTER TABLE authors 
        ALTER COLUMN id 
        DROP DEFAULT
    ''')
    
    # Удаляем последовательность
    op.execute('DROP SEQUENCE IF EXISTS authors_id_seq') 