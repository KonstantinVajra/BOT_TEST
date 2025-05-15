from sqlalchemy import create_engine
import urllib.parse
from src.models import Base

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
    
    # Test connection
    with engine.connect() as conn:
        print("Successfully connected to database!")
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("Successfully created all tables!")
    
except Exception as e:
    print(f"Error: {e}") 