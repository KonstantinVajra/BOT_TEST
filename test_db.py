from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

try:
    # Create connection parameters
    params = {
        'host': '46.19.64.78',
        'port': '5432',
        'database': 'default_db',
        'user': 'gen_user',
        'password': ',Pw0VjKC\\Y\\2?P'
    }
    
    # Create connection URL
    url = f"postgresql://{params['user']}:{urllib.parse.quote_plus(params['password'])}@{params['host']}:{params['port']}/{params['database']}"
    print(f"Attempting to connect with URL: {url}")
    
    # Try to connect
    engine = create_engine(url)
    with engine.connect() as conn:
        print("Successfully connected to database!")
        # Test query
        result = conn.execute("SELECT 1").scalar()
        print(f"Test query result: {result}")
        
except Exception as e:
    print(f"Error: {e}") 