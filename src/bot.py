import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot import types
from typing import Optional, Dict
from src.models import Author, Review, Media, Category
from datetime import datetime, timedelta
import logging
import os
import atexit
import time
from telebot.apihelper import ApiTelegramException

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

LOCK_FILE = "bot.lock"

def check_bot_instance():
    """Check if another bot instance is running"""
    if os.path.exists(LOCK_FILE):
        logger.error("Another bot instance is already running!")
        return False
    
    # Create lock file
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True

def cleanup_lock():
    """Remove lock file on exit"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception as e:
        logger.error(f"Failed to remove lock file: {e}")

# Register cleanup function
atexit.register(cleanup_lock)

def transliterate(text: str) -> str:
    # Простая транслитерация для команд
    ru_en = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    return ''.join(ru_en.get(c.lower(), c) for c in text)

class ReviewStates(StatesGroup):
    collecting_reviews = State()

class ReviewBot:
    def __init__(self, token: str, admin_id: int, db_session):
        """Initialize bot with token and admin user id"""
        self.bot = telebot.TeleBot(
            token,
            state_storage=StateMemoryStorage(),
            parse_mode='HTML',
            threaded=True
        )
        self.admin_id = admin_id
        self.db = db_session
        self.current_selection: Dict[int, dict] = {}  # Store current user selections
        self.category_commands = {}  # Store mapping between commands and categories
        self.message_buffer = []  # Буфер для накопления сообщений
        self.max_buffer_size = 100  # Максимальный размер буфера
        self.setup_handlers()
        logger.info(f"Бот инициализирован с admin_id: {admin_id}")

    def setup_commands(self):
        # Get all categories for menu commands
        categories = self.db.query(Category.name).distinct().all()
        categories = sorted(cat[0] for cat in categories)
        
        commands = [
            types.BotCommand("start", "Запустить бота и показать справку"),
            types.BotCommand("cat", "Показать список категорий"),
            types.BotCommand("save", "Сохранить накопленные отзывы в базу"),
            types.BotCommand("clear", "Очистить буфер сообщений")
        ]
        
        # Add command for each category
        for category in categories:
            cmd = f"list_{transliterate(category)}"
            self.category_commands[cmd] = category
            commands.append(
                types.BotCommand(cmd, f"Показать список объектов категории '{category}'")
            )
            
        self.bot.set_my_commands(commands)

    def setup_handlers(self):
        # Command handlers
        self.bot.message_handler(commands=['start', 'help'])(self.handle_start)
        self.bot.message_handler(commands=['cat'])(self.handle_categories)
        self.bot.message_handler(commands=['save'])(self.handle_save_buffer)
        self.bot.message_handler(commands=['clear'])(self.handle_clear_buffer)
        self.bot.message_handler(commands=['stop'])(self.handle_stop)
        
        # Dynamic category handlers
        categories = self.db.query(Category.name).distinct().all()
        for category in categories:
            cmd = f"list_{transliterate(category[0])}"
            self.category_commands[cmd] = category[0]
            self.bot.message_handler(commands=[cmd])(self.handle_list_items)
        
        # Handle item selection via deep linking
        self.bot.message_handler(func=lambda message: message.text and message.text.startswith('/select_'))(self.handle_select)
        
        # Message handlers for collecting reviews - handle all messages from admin
        self.bot.message_handler(
            func=lambda message: message.from_user.id == self.admin_id,
            content_types=['text', 'photo', 'video', 'voice', 'document', 'audio', 'animation']
        )(self.buffer_review)

        # Add debug handler for all other messages
        @self.bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'voice', 'document', 'audio', 'sticker', 'animation'])
        def debug_handler(message):
            current_state = self.bot.get_state(message.from_user.id, message.chat.id)
            logger.info(f"=== INCOMING MESSAGE ===")
            logger.info(f"From user: {message.from_user.id} ({message.from_user.first_name})")
            logger.info(f"Message ID: {message.message_id}")
            logger.info(f"Content type: {message.content_type}")
            logger.info(f"Is forwarded: {message.forward_from is not None}")
            if message.forward_from:
                logger.info(f"Forwarded from: {message.forward_from.id} ({message.forward_from.first_name})")
            logger.info(f"Current state: {current_state}")
            logger.info(f"Has text: {bool(message.text)}")
            logger.info(f"Has caption: {bool(message.caption)}")
            logger.info(f"Has photo: {bool(message.photo)}")
            logger.info(f"Has video: {bool(message.video)}")
            logger.info(f"Has voice: {bool(message.voice)}")
            logger.info(f"Has document: {bool(message.document)}")
            logger.info(f"Has audio: {bool(message.audio)}")
            logger.info(f"Has sticker: {bool(message.sticker)}")
            logger.info(f"Has animation: {bool(message.animation)}")
            logger.info("=== END INCOMING MESSAGE ===\n")

    def handle_start(self, message):
        if message.from_user.id != self.admin_id:
            self.bot.reply_to(message, "Извините, вы не являетесь администратором бота.")
            return

        self.message_buffer = []  # Очищаем буфер при старте
        self.bot.reply_to(
            message,
            "Бот для сбора отзывов запущен.\n\n"
            "Доступные команды:\n"
            "/cat - показать список категорий\n"
            "/save - сохранить накопленные отзывы в базу\n"
            "/clear - очистить буфер сообщений\n"
            "Для каждой категории есть своя команда в меню команд.\n"
            "/stop - закончить сбор отзывов\n"
            "/help - показать эту справку"
        )

    def handle_categories(self, message):
        if message.from_user.id != self.admin_id:
            return

        # Get all categories
        categories = self.db.query(Category.name).distinct().all()
        categories = sorted(cat[0] for cat in categories)
        
        response = "Доступные категории:\n\n"
        for category in categories:
            cmd = f"list_{transliterate(category)}"
            response += f"• /{cmd} - показать объекты категории '{category}'\n"

        self.bot.reply_to(message, response)

    def handle_list_items(self, message):
        if message.from_user.id != self.admin_id:
            return

        # Extract category from command
        cmd = message.text.split('@')[0][1:]  # Remove / and possible @botname
        category = self.category_commands.get(cmd)
        if not category:
            return
        
        # Get items for selected category
        items = self.db.query(Category.item_name)\
            .filter(Category.name == category)\
            .order_by(Category.item_name)\
            .all()
        
        if not items:
            self.bot.reply_to(
                message,
                f"Категория '{category}' не найдена или в ней нет объектов.\n"
                f"Используйте /cat для просмотра доступных категорий."
            )
            return

        items = [item[0] for item in items]
        
        response = f"Объекты в категории '{category}':\n\n"
        for i, item in enumerate(items, 1):
            # Create a deep link for each item
            cmd = f"select_{transliterate(category)}_{i}"
            response += f"{i}. /{cmd} - {item}\n"

        self.bot.reply_to(message, response)

    def handle_select(self, message):
        if message.from_user.id != self.admin_id:
            return

        # Extract category and item number from deep link
        parts = message.text.split('@')[0][1:].split('_')  # Remove / and possible @botname
        if len(parts) != 3:
            return

        # Find original category name
        for cmd, cat in self.category_commands.items():
            if cmd.endswith(parts[1]):
                category = cat
                break
        else:
            return

        try:
            item_number = int(parts[2])
        except ValueError:
            return

        # Get items for selected category
        items = self.db.query(Category.item_name)\
            .filter(Category.name == category)\
            .order_by(Category.item_name)\
            .all()
        
        if not items:
            return

        items = [item[0] for item in items]
        
        if item_number < 1 or item_number > len(items):
            return

        item = items[item_number - 1]
        
        # Store selection
        self.current_selection[message.from_user.id] = {
            'category': category,
            'item': item
        }

        self.bot.reply_to(
            message,
            f"✅ Выбрано:\n"
            f"Категория: {category}\n"
            f"Объект: {item}\n\n"
            f"Теперь пересылайте сюда отзывы.\n"
            f"Для завершения сбора отзывов используйте /stop"
        )
        
        # Set state
        self.bot.set_state(message.from_user.id, ReviewStates.collecting_reviews, message.chat.id)

    def check_message_duplicate(self, message):
        """Проверяет, не было ли это сообщение уже переслано ранее"""
        return False  # Всегда возвращаем False, чтобы сохранять все сообщения

    def buffer_review(self, message):
        """Add message to buffer for batch processing"""
        logger.info("=== START BUFFERING MESSAGE ===")
        logger.info(f"Message ID: {message.message_id}")
        logger.info(f"Message type: {message.content_type}")
        
        # Добавляем расширенное логирование для пересланных сообщений
        if message.forward_from_message_id:
            logger.info(f"Original message ID: {message.forward_from_message_id}")
        if message.forward_date:
            logger.info(f"Forward date: {message.forward_date}")
        if message.forward_from:
            logger.info(f"Forwarded from user: {message.forward_from.id} ({message.forward_from.first_name})")
        if message.forward_from_chat:
            logger.info(f"Forwarded from chat: {message.forward_from_chat.id} ({message.forward_from_chat.title})")
        
        # Остальной код остается без изменений
        if len(self.message_buffer) >= self.max_buffer_size:
            logger.warning(f"Buffer is full ({self.max_buffer_size} messages). Please save current buffer first.")
            self.bot.reply_to(
                message, 
                f"⚠️ Буфер заполнен ({self.max_buffer_size} сообщений).\n"
                "Пожалуйста, сохраните текущие отзывы командой /save"
            )
            return

        if message.text:
            logger.info(f"Text content: {message.text[:100]}")
        if message.caption:
            logger.info(f"Caption content: {message.caption[:100]}")
        if message.forward_from:
            logger.info(f"Forwarded from: {message.forward_from.id} ({message.forward_from.first_name})")
        if message.photo:
            logger.info(f"Has photo: {len(message.photo)} sizes")
        if message.video:
            logger.info("Has video")
            if message.video.file_size:
                logger.info(f"Video size: {message.video.file_size} bytes")
        if message.voice:
            logger.info("Has voice message")
        if message.document:
            logger.info(f"Has document: {message.document.file_name}")
        if message.audio:
            logger.info("Has audio")
        if message.animation:
            logger.info("Has animation (GIF)")

        selection = self.current_selection.get(message.from_user.id)
        if not selection:
            logger.warning("No category/item selected - skipping")
            self.bot.reply_to(message, "Сначала выберите категорию и объект через меню.")
            return

        logger.info(f"Adding to buffer: {selection['category']} - {selection['item']}")
        
        # Добавляем сообщение в буфер вместе с информацией о категории и объекте
        self.message_buffer.append({
            'message': message,
            'category': selection['category'],
            'item': selection['item']
        })
        
        buffer_size = len(self.message_buffer)
        logger.info(f"Current buffer size: {buffer_size}")
        
        # Показываем статус каждые 5 сообщений или когда буфер почти полон
        if buffer_size % 5 == 0 or buffer_size >= self.max_buffer_size * 0.9:
            # Анализируем содержимое буфера
            text_msgs = sum(1 for m in self.message_buffer if (m['message'].text or m['message'].caption))
            photo_msgs = sum(1 for m in self.message_buffer if m['message'].photo)
            video_msgs = sum(1 for m in self.message_buffer if m['message'].video)
            voice_msgs = sum(1 for m in self.message_buffer if m['message'].voice)
            doc_msgs = sum(1 for m in self.message_buffer if m['message'].document)
            audio_msgs = sum(1 for m in self.message_buffer if m['message'].audio)
            anim_msgs = sum(1 for m in self.message_buffer if m['message'].animation)
            
            status_msg = f"✅ В буфере {buffer_size} сообщений:\n"
            status_msg += f"• Текст: {text_msgs}\n"
            status_msg += f"• Фото: {photo_msgs}\n"
            status_msg += f"• Видео: {video_msgs}\n"
            status_msg += f"• Голос: {voice_msgs}\n"
            if doc_msgs: status_msg += f"• Документы: {doc_msgs}\n"
            if audio_msgs: status_msg += f"• Аудио: {audio_msgs}\n"
            if anim_msgs: status_msg += f"• GIF: {anim_msgs}\n"
            status_msg += f"\nКатегория: {selection['category']}\n"
            status_msg += f"Объект: {selection['item']}\n"
            
            # Добавляем предупреждение, если буфер почти полон
            if buffer_size >= self.max_buffer_size * 0.9:
                status_msg += f"\n⚠️ Буфер почти полон! Максимум: {self.max_buffer_size}"
            
            status_msg += "\nИспользуйте /save для сохранения в базу"
            
            self.bot.reply_to(message, status_msg)
            logger.info(f"Buffer contains: {text_msgs} text, {photo_msgs} photo, {video_msgs} video, {voice_msgs} voice, {doc_msgs} doc, {audio_msgs} audio, {anim_msgs} animation messages")

    def handle_save_buffer(self, message):
        """Save all buffered messages to database"""
        logger.info("=== START SAVING BUFFER ===")
        logger.info(f"Current buffer size: {len(self.message_buffer)}")
        logger.info("Message types in buffer:")
        for idx, item in enumerate(self.message_buffer):
            msg = item['message']
            logger.info(f"{idx+1}. Type: {msg.content_type}, From: {msg.forward_from.first_name if msg.forward_from else 'Unknown'}")
        
        if message.from_user.id != self.admin_id:
            logger.warning(f"Unauthorized save attempt from user {message.from_user.id}")
            return

        if not self.message_buffer:
            logger.warning("Buffer is empty - nothing to save")
            self.bot.reply_to(message, "Буфер пуст. Нечего сохранять.")
            return

        buffer_size = len(self.message_buffer)
        logger.info(f"Starting to save {buffer_size} messages")
        
        # Анализируем содержимое буфера перед сохранением
        text_msgs = sum(1 for m in self.message_buffer if (m['message'].text or m['message'].caption))
        photo_msgs = sum(1 for m in self.message_buffer if m['message'].photo)
        video_msgs = sum(1 for m in self.message_buffer if m['message'].video)
        voice_msgs = sum(1 for m in self.message_buffer if m['message'].voice)
        doc_msgs = sum(1 for m in self.message_buffer if m['message'].document)
        audio_msgs = sum(1 for m in self.message_buffer if m['message'].audio)
        anim_msgs = sum(1 for m in self.message_buffer if m['message'].animation)
        
        logger.info(f"Buffer contains: {text_msgs} text, {photo_msgs} photo, {video_msgs} video, {voice_msgs} voice, {doc_msgs} doc, {audio_msgs} audio, {anim_msgs} animation messages")

        try:
            saved_count = 0
            errors_count = 0
            authors_cache = {}  # Кэш для авторов
            media_saved = 0

            for idx, item in enumerate(self.message_buffer, 1):
                try:
                    msg = item['message']
                    logger.info(f"\nProcessing message {idx}/{buffer_size}")
                    logger.info(f"Category: {item['category']}, Item: {item['item']}")
                    logger.info(f"Message type: {msg.content_type}")
                    
                    # Получаем или создаем автора из кэша
                    if msg.forward_from:
                        # Обычное пересланное сообщение
                        author_id = msg.forward_from.id
                        author_name = msg.forward_from.first_name
                        author_username = msg.forward_from.username
                    elif msg.forward_from_chat:
                        # Автор скрыл свой профиль
                        author_id = 0  # Специальный ID для анонимных авторов
                        author_name = "аноним"
                        author_username = None
                    else:
                        # Не пересланное сообщение
                        author_id = msg.from_user.id
                        author_name = msg.from_user.first_name
                        author_username = msg.from_user.username

                    if author_id not in authors_cache:
                        logger.info(f"Looking up author {author_id}")
                        author = self.db.query(Author).filter_by(telegram_id=author_id).first()
                        if not author:
                            logger.info(f"Creating new author: {author_name}")
                            author = Author(
                                telegram_id=author_id,
                                username=author_username,
                                display_name=author_name or 'аноним'
                            )
                            self.db.add(author)
                            self.db.commit()
                            logger.info(f"Created author with ID: {author.id}")
                        else:
                            logger.info(f"Found existing author with ID: {author.id}")
                        authors_cache[author_id] = author
                    
                    author = authors_cache[author_id]

                    # Создаем отзыв
                    review_text = msg.text if msg.text else msg.caption
                    logger.info(f"Creating review. Text preview: {review_text[:50] if review_text else 'No text'}")
                    
                    review = Review(
                        text=review_text,
                        category=item['category'],
                        reference_name=item['item'],
                        author=author,
                        timestamp=datetime.fromtimestamp(msg.date)
                    )
                    self.db.add(review)
                    self.db.commit()
                    logger.info(f"Created review with ID: {review.id}")

                    # Обрабатываем медиафайлы
                    media_added = False
                    
                    if msg.photo:
                        logger.info(f"Processing photo attachment with {len(msg.photo)} sizes")
                        media = Media(
                            file_id=msg.photo[-1].file_id,
                            file_type='photo',
                            review=review,
                            context_text=msg.caption
                        )
                        self.db.add(media)
                        media_added = True
                        
                    elif msg.video:
                        logger.info("Processing video attachment")
                        media = Media(
                            file_id=msg.video.file_id,
                            file_type='video',
                            review=review,
                            context_text=msg.caption
                        )
                        self.db.add(media)
                        media_added = True
                        
                    elif msg.voice:
                        logger.info("Processing voice message")
                        media = Media(
                            file_id=msg.voice.file_id,
                            file_type='voice',
                            review=review,
                            context_text=None
                        )
                        self.db.add(media)
                        media_added = True
                        
                    elif msg.document:
                        logger.info(f"Processing document: {msg.document.file_name}")
                        media = Media(
                            file_id=msg.document.file_id,
                            file_type='document',
                            review=review,
                            context_text=msg.caption
                        )
                        self.db.add(media)
                        media_added = True
                        
                    elif msg.audio:
                        logger.info("Processing audio file")
                        media = Media(
                            file_id=msg.audio.file_id,
                            file_type='audio',
                            review=review,
                            context_text=msg.caption
                        )
                        self.db.add(media)
                        media_added = True
                        
                    elif msg.animation:
                        logger.info("Processing animation (GIF)")
                        media = Media(
                            file_id=msg.animation.file_id,
                            file_type='animation',
                            review=review,
                            context_text=msg.caption
                        )
                        self.db.add(media)
                        media_added = True

                    if media_added:
                        self.db.commit()
                        media_saved += 1
                        logger.info("Saved media attachment")

                    saved_count += 1
                    
                    # Показываем прогресс каждые 5 сообщений
                    if saved_count % 5 == 0:
                        progress_msg = (
                            f"⏳ Прогресс: {saved_count}/{buffer_size}\n"
                            f"Сохранено медиафайлов: {media_saved}"
                        )
                        self.bot.reply_to(message, progress_msg)
                        logger.info(f"Progress update: {progress_msg}")

                except Exception as e:
                    logger.error(f"Error processing message {idx}: {str(e)}", exc_info=True)
                    errors_count += 1
                    continue

            # Очищаем буфер
            self.message_buffer = []
            
            status_msg = (
                f"✅ Сохранение завершено\n"
                f"Всего сообщений: {buffer_size}\n"
                f"Успешно сохранено: {saved_count}\n"
                f"Медиафайлов сохранено: {media_saved}\n"
                f"Ошибок: {errors_count}"
            )
            
            self.bot.reply_to(message, status_msg)
            logger.info(f"Finished saving buffer: {status_msg}")

        except Exception as e:
            logger.error(f"Critical error in batch save: {str(e)}", exc_info=True)
            self.bot.reply_to(
                message,
                f"❌ Произошла критическая ошибка при сохранении: {str(e)}\n"
                f"Успешно сохранено: {saved_count}\n"
                f"Медиафайлов сохранено: {media_saved}"
            )
        
        logger.info("=== END SAVING BUFFER ===\n")

    def handle_clear_buffer(self, message):
        """Clear message buffer"""
        if message.from_user.id != self.admin_id:
            return

        count = len(self.message_buffer)
        self.message_buffer = []
        self.bot.reply_to(message, f"Буфер очищен. Удалено {count} сообщений.")

    def handle_stop(self, message):
        if message.from_user.id != self.admin_id:
            return

        # Clear user state and selection
        self.bot.delete_state(message.from_user.id, message.chat.id)
        if message.from_user.id in self.current_selection:
            del self.current_selection[message.from_user.id]

        self.bot.reply_to(
            message,
            "Сбор отзывов завершен.\n"
            "Для начала нового сбора используйте:\n"
            "/cat - показать категории\n"
            "Для каждой категории есть своя команда в меню команд.\n"
            "/stop - закончить сбор отзывов\n"
            "/help - показать эту справку"
        )

    def run(self):
        """Run the bot"""
        try:
            logger.info("Starting bot polling...")
            self.setup_commands()  # Устанавливаем команды после успешного запуска
            self.bot.polling(non_stop=True, interval=3)
        except Exception as e:
            logger.error(f"Error in bot polling: {e}")
            if isinstance(e, ApiTelegramException) and e.error_code == 401:
                logger.error("Unauthorized error - check bot token")
            raise
        finally:
            cleanup_lock()
            logger.info("Bot shutdown complete.") 