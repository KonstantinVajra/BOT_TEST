from sqlalchemy import create_engine, text
import urllib.parse

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

try:
    # Create engine
    engine = create_engine(url)
    
    # Execute query
    with engine.connect() as conn:
        # Get distinct categories
        categories = conn.execute(text("SELECT DISTINCT name FROM categories ORDER BY name")).fetchall()
        
        print("\nСписок категорий и их объектов:")
        for category in categories:
            print(f"\n{category[0]}:")
            # Get items for this category
            items = conn.execute(
                text("SELECT item_name FROM categories WHERE name = :name ORDER BY item_name"),
                {"name": category[0]}
            ).fetchall()
            for item in items:
                print(f"  - {item[0]}")
            
except Exception as e:
    print(f"Ошибка: {e}") 