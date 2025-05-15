import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from src.models import Author, Review, Media, ReviewCategory
from src.bot import ReviewBot

class MockPhotoSize:
    def __init__(self, file_id="test_file_id"):
        self.file_id = file_id

class MockMessage:
    def __init__(self, text=None, from_user=None, forward_from=None, 
                 photo=None, video=None, voice=None, caption=None, 
                 date=None, message_id=None):
        self.text = text
        self.from_user = from_user
        self.forward_from = forward_from
        self.photo = [MockPhotoSize()] if photo else None
        self.video = MockPhotoSize() if video else None
        self.voice = MockPhotoSize() if voice else None
        self.caption = caption
        self.date = date or datetime.now()
        self.message_id = message_id or 1

class MockUser:
    def __init__(self, id):
        self.id = id

class MockQuery:
    def __init__(self, session, model):
        self.session = session
        self.model = model
        self.filters = []
        
    def filter(self, *args):
        self.filters.extend(args)
        return self
        
    def filter_by(self, **kwargs):
        return self
        
    def first(self):
        # For Author queries
        if self.model == Author:
            return None
            
        # For Review queries with time filters
        if self.model == Review and self.filters:
            # Find the most recent review in the session
            reviews = [obj for obj in self.session.added if isinstance(obj, Review)]
            if reviews:
                return reviews[-1]
        return None

@pytest.fixture
def mock_db_session():
    class MockSession:
        def __init__(self):
            self.added = []
            self.committed = False
            
        def add(self, obj):
            self.added.append(obj)
            
        def commit(self):
            self.committed = True
            
        def query(self, model):
            return MockQuery(self, model)
    
    return MockSession()

@pytest.fixture
def bot(mock_db_session):
    return ReviewBot(token="test_token", admin_id=123, db_session=mock_db_session)

def test_photo_without_caption_has_context_from_neighboring_text(bot, mock_db_session):
    # Arrange
    author_id = 456
    admin_id = 123
    base_time = datetime(2023, 1, 1, 12, 0)
    
    with freeze_time(base_time):
        # First, send a text message
        text_msg = MockMessage(
            text="Отличный отель! Очень чисто и уютно.",
            from_user=MockUser(admin_id),
            forward_from=MockUser(author_id),
            date=base_time
        )
        
        # Then, send a photo without caption
        photo_msg = MockMessage(
            photo=[MockPhotoSize()],
            from_user=MockUser(admin_id),
            forward_from=MockUser(author_id),
            date=base_time + timedelta(seconds=30)
        )
        
        # Act
        bot.handle_message(text_msg)
        bot.handle_message(photo_msg)
        
        # Assert
        assert len(mock_db_session.added) == 3  # Author, Review, and Media
        saved_review = next(obj for obj in mock_db_session.added if isinstance(obj, Review))
        saved_media = next(obj for obj in mock_db_session.added if isinstance(obj, Media))
        
        assert saved_review.text == "Отличный отель! Очень чисто и уютно."
        assert saved_review.category == ReviewCategory.HOTEL
        assert saved_media.review_id == saved_review.id

def test_detect_review_category_from_keywords(bot, mock_db_session):
    # Arrange
    text = "Экскурсия была просто потрясающая!"  # Убрали упоминание гида
    msg = MockMessage(
        text=text,
        from_user=MockUser(123),
        forward_from=MockUser(456)
    )
    
    # Act
    bot.handle_message(msg)
    
    # Assert
    saved_review = next(obj for obj in mock_db_session.added if isinstance(obj, Review))
    assert saved_review.category == ReviewCategory.EXCURSION

def test_multiple_media_single_review(bot, mock_db_session):
    # Arrange
    author_id = 456
    admin_id = 123
    base_time = datetime(2023, 1, 1, 12, 0)
    
    with freeze_time(base_time):
        # Send text
        text_msg = MockMessage(
            text="Ресторан превзошел все ожидания!",
            from_user=MockUser(admin_id),
            forward_from=MockUser(author_id),
            date=base_time
        )
        
        # Send multiple photos
        photo_msg1 = MockMessage(
            photo=[MockPhotoSize()],
            from_user=MockUser(admin_id),
            forward_from=MockUser(author_id),
            date=base_time + timedelta(seconds=30)
        )
        
        photo_msg2 = MockMessage(
            photo=[MockPhotoSize()],
            from_user=MockUser(admin_id),
            forward_from=MockUser(author_id),
            date=base_time + timedelta(seconds=60)
        )
        
        # Act
        bot.handle_message(text_msg)
        bot.handle_message(photo_msg1)
        bot.handle_message(photo_msg2)
        
        # Assert
        saved_review = next(obj for obj in mock_db_session.added if isinstance(obj, Review))
        media_items = [obj for obj in mock_db_session.added if isinstance(obj, Media)]
        
        assert len(media_items) == 2
        assert all(media.review_id == saved_review.id for media in media_items)
        assert saved_review.category == ReviewCategory.RESTAURANT 