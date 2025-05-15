from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command
import urllib.parse
import os
import tempfile

# Database connection parameters
params = {
    'host': '46.19.64.78',
    'port': '5432',
    'database': 'default_db',
    'user': 'gen_user',
    'password': ',Pw0VjKC\\Y\\2?P'
}

# Create connection URL
engine = create_engine(
    'postgresql://',
    connect_args={
        'host': params['host'],
        'port': params['port'],
        'database': params['database'],
        'user': params['user'],
        'password': params['password']
    }
)

try:
    # Test connection
    with engine.connect() as conn:
        print("Successfully connected to database!")
    
    # Create temporary alembic.ini
    temp_config = f"""[alembic]
script_location = migrations
sqlalchemy.url = postgresql://{params['user']}:{urllib.parse.quote_plus(params['password'])}@{params['host']}:{params['port']}/{params['database']}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
    
    # Write temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as temp_file:
        temp_file.write(temp_config)
        temp_file_path = temp_file.name
    
    # Apply migrations using temporary config
    alembic_cfg = Config(temp_file_path)
    command.upgrade(alembic_cfg, "head")
    print("Migrations successfully applied!")
    
    # Cleanup
    os.unlink(temp_file_path)
    
except Exception as e:
    print(f"Error: {e}")
    # Ensure cleanup in case of error
    if 'temp_file_path' in locals():
        try:
            os.unlink(temp_file_path)
        except:
            pass 