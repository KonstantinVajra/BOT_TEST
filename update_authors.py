from sqlalchemy import create_engine, text

# Подключение к базе данных
engine = create_engine('postgresql://gen_user:test12345@46.19.64.78:5432/default_db')

# SQL команды для обновления
commands = [
    # Создаем sequence если её нет
    'CREATE SEQUENCE IF NOT EXISTS authors_id_seq',
    
    # Устанавливаем текущее значение
    'SELECT setval(\'authors_id_seq\', (SELECT MAX(id) FROM authors))',
    
    # Меняем колонку id на использование sequence
    'ALTER TABLE authors ALTER COLUMN id SET DEFAULT nextval(\'authors_id_seq\')',
    
    # Добавляем UNIQUE constraint для telegram_id если его нет
    '''
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'uq_authors_telegram_id'
        ) THEN
            ALTER TABLE authors ADD CONSTRAINT uq_authors_telegram_id UNIQUE (telegram_id);
        END IF;
    END
    $$;
    ''',
    
    # Делаем telegram_id NOT NULL
    'ALTER TABLE authors ALTER COLUMN telegram_id SET NOT NULL'
]

# Выполняем команды
with engine.connect() as conn:
    for cmd in commands:
        try:
            conn.execute(text(cmd))
            conn.commit()
            print(f"Успешно выполнено: {cmd[:50]}...")
        except Exception as e:
            print(f"Ошибка при выполнении: {cmd[:50]}...")
            print(f"Ошибка: {str(e)}")
            
print("\nОбновление завершено!") 