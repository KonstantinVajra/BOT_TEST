import os
from dotenv import load_dotenv
from src.bot import ReviewBot
from src.database import get_db

def main():
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN")
    admin_id = int(os.getenv("ADMIN_ID"))
    
    if not bot_token or not admin_id:
        raise ValueError("BOT_TOKEN and ADMIN_ID must be set in .env file")
    
    db = next(get_db())
    bot = ReviewBot(token=bot_token, admin_id=admin_id, db_session=db)
    
    try:
        print("Bot started. Press Ctrl+C to stop.")
        bot.run()
    except KeyboardInterrupt:
        print("Bot stopped.")
    finally:
        db.close()

if __name__ == "__main__":
    main() 