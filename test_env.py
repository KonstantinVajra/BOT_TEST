import os
from dotenv import load_dotenv

load_dotenv()

print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))
print("ADMIN_ID:", os.getenv("ADMIN_ID"))
print("DATABASE_URL:", os.getenv("DATABASE_URL")) 