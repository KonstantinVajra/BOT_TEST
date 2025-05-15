from src.database import get_db
from sqlalchemy import text
import sys

def main():
    db = next(get_db())
    
    try:
        print("\nПроверка прав в базе данных...")
        
        # Проверяем права на создание таблиц
        result = db.execute(text("""
            SELECT table_name, privilege_type
            FROM information_schema.table_privileges 
            WHERE grantee = CURRENT_USER
            AND table_schema = 'public'
        """)).fetchall()
        
        print("\nПрава на таблицы:")
        for table, privilege in result:
            print(f"- {table}: {privilege}")
            
        # Проверяем существование таблиц
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """)).fetchall()
        
        print("\nСуществующие таблицы:")
        for (table,) in result:
            print(f"- {table}")
            
    except Exception as e:
        print(f"\n❌ Ошибка при проверке прав: {str(e)}", file=sys.stderr)
    finally:
        db.close()

if __name__ == "__main__":
    main() 