from sqlalchemy import create_engine, text
from src.models import Author, Review, Media, Base

# Connection string
DATABASE_URL = "postgresql://gen_user:%2CPw0VjKC%5CY%5C2%3FP@46.19.64.78:5432/default_db"

def check_database():
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Try to connect and get counts
        with engine.connect() as connection:
            # Check authors
            result = connection.execute(text("SELECT COUNT(*) FROM authors"))
            authors_count = result.scalar()
            print(f"Authors count: {authors_count}")
            
            # Check reviews
            result = connection.execute(text("SELECT COUNT(*) FROM reviews"))
            reviews_count = result.scalar()
            print(f"Reviews count: {reviews_count}")
            
            # Check media
            result = connection.execute(text("SELECT COUNT(*) FROM media"))
            media_count = result.scalar()
            print(f"Media count: {media_count}")
            
            # Get latest entries if any exist
            if reviews_count > 0:
                print("\nLatest review:")
                result = connection.execute(text("""
                    SELECT r.id, r.text, r.category, r.reference_name, 
                           a.display_name, r.timestamp
                    FROM reviews r
                    JOIN authors a ON r.author_id = a.id
                    ORDER BY r.timestamp DESC
                    LIMIT 1
                """))
                review = result.fetchone()
                if review:
                    print(f"ID: {review[0]}")
                    print(f"Text: {review[1]}")
                    print(f"Category: {review[2]}")
                    print(f"Reference: {review[3]}")
                    print(f"Author: {review[4]}")
                    print(f"Time: {review[5]}")

    except Exception as e:
        print(f"Error checking database: {str(e)}")

if __name__ == "__main__":
    check_database() 