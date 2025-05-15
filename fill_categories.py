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

# Данные для заполнения
categories_data = {
    "отель": [
        "Arenas Doradas", "Barcelo Solymar", "Blau Varadero", "Brisas Santa Lucia",
        "Brisas del Caribe", "Gran Caribe Vigia", "Grand Aston Paredon",
        "Grand Muthu Cayo Guillermo", "GrandMemories & Santuari", "Hotel Caracol / Камагуэй",
        "Iberostar Bella Costa", "Iberostar Bella Vista", "Iberostar Laguna Azul",
        "Iberostar Playa Alameda", "Iberostar Selection", "Iberostar Tainos",
        "Kempinsky Manzana Havana", "Las Morals", "Los Cactus Varadero",
        "Melia International", "Melia Las Americas", "Melia Las Antillas",
        "Melia Marina Varadero", "Melia Peninsula", "Melia Varadero",
        "Memories Caribe Beach", "Memories Jibacoa", "Mistique Casa Perla",
        "Muthu Playa Varadero", "Occidental Arenas Blancas", "Palma Real",
        "Paradisus Princess", "Paradisus Varadero", "Playa Vista Azul",
        "Puntarena", "Resonans Memoris Varadero", "Roc Arenas Doradas",
        "Roc Barlovento", "Roc Varadero", "Royalton Hicacos",
        "Royalty Havana Paseo", "Selectim Family Resort Varadero",
        "Sirenis Tropical Varadero", "Sol Caribe Beach", "Sol Cayo Coco",
        "Sol Palmeras", "Sol Varadero", "Starfish Cuatro Palmas",
        "Starfish Varadero", "Tryp Cayo Coco", "Tuxpan Hotel",
        "Valentin el Patriarca", "Villa Cuba", "Villa Tortuga",
        "Woovo Playa Hermosa Cayo Paredon"
    ],
    "гид": [
        "Александр. Гавана", "Вивьен. Гавана", "Галина. Варадеро",
        "Глэдис Кристина. Гавана", "Давид и Полина. Варадеро",
        "Ирина Каскарет. Гавана", "Карлос Варадеро", "Карлос Луис. Варадеро",
        "Квинтин. Варадеро", "Леонель. Варадеро", "Луис. Кайо Коко",
        "Любовь Шкатова. Варадеро", "Людмила Зенкова. Варадеро",
        "Людмила Морехон. Варадеро", "Мирея Варадеро", "Орландо. Варадеро",
        "Освальдо. Варадеро", "Раиса. Гавана", "Роландо. Варадеро",
        "Феликс Луис. Кайо Коко", "Франк. Варадеро", "Франк. Кайо Коко",
        "Хесус Соккарас. Варадеро", "Хуан Карлос. Гавана", "Хулия. Гид. Гавана",
        "Энрике. Варадеро"
    ],
    "ресторан": [
        "43.5 (43я улица)", "Bar Galeón (53я улица)", "Beatles Bar",
        "Bolshoi (62я улица)", "Casa de Al. Аль Капоне (1я улица)",
        "Castell Nuovo Terazza", "Compas Bar (34я улица)", "Don Alex (31я улица)",
        "El Aljibe", "El Ancla (62я улица)", "El Caney (40я улица)",
        "El Criollo (18я улица)", "El Melaito", "El Rancho (58я улица)",
        "El Toro (25я улица)", "La Barbacoa", "La Cava (62 улица)",
        "La Terazza Cuba (18я улица)", "La Vaca Rosада. Розовая Корова (21я ул)",
        "La Vicaria (38я улица)", "La bodeguita del medio (Varadero 40я ул)",
        "La gruta del vino (59я улица. В парке Хосоне)", "La rampa (43я улица)",
        "Marisquería Laurent (31я улица)", "Mistique Casa Perla",
        "Pina Colada La Vigia", "Rigo's pizza", "Salsa Suarez (31я улица)",
        "Varadero 60 (60я улица)", "Vernissage (36я улица)", "Wacos Club",
        "Бар Floridita", "Бар клуб Calle 62 (62я улица)", "Вилла Дюпона. Коктейли",
        "Клуб La Comparсita", "Пивоварня Factoria 43", "Рудольфо и его лобстеры (28я-29я)"
    ],
    "экскурсия": [
        "Авторские рассказы", "Дискавери тур. Джип сафари",
        "Индивидуальная яхта. Кайо Бланко", "Общий катамаран Варадеро",
        "Разное", "Самостоятельные экскурсии", "Цены экскурсий",
        "Экскурсии Кайо Коко", "Экскурсии Матанзас", "Экскурсии в Варадеро",
        "Экскурсии в Виньялес", "Экскурсии. Разные отзывы", "Экскурсия в Гавану",
        "Экскурсия в Тринидад и Эль Ничо", "Экскурсия на Карибы"
    ],
    "пляж": [
        "пляж Arenas Doradas", "пляж Barcelo Solymar", "пляж Blau Varadero",
        "пляж Brisas Santa Lucia", "пляж Brisas del Caribe", "пляж Gran Caribe Vigia",
        "пляж Grand Aston Paredon", "пляж Grand Muthu Cayo Guillermo",
        "пляж GrandMemories & Santuari", "пляж Hotel Caracol / Камагуэй",
        "пляж Iberostar Bella Costa", "пляж Iberostar Bella Vista",
        "пляж Iberostar Laguna Azul", "пляж Iberostar Playa Alameda",
        "пляж Iberostar Selection", "пляж Iberostar Tainos",
        "пляж Kempinsky Manzana Havana", "пляж Las Morals",
        "пляж Los Cactus Varadero", "пляж Melia International",
        "пляж Melia Las Americas", "пляж Melia Las Antillas",
        "пляж Melia Marina Varadero", "пляж Melia Peninsula",
        "пляж Melia Varadero", "пляж Memories Caribe Beach",
        "пляж Memories Jibacoa", "пляж Mistique Casa Perla",
        "пляж Muthu Playa Varadero", "пляж Occidental Arenas Blancas",
        "пляж Palma Real", "пляж Paradisus Princess",
        "пляж Paradisus Varadero", "пляж Playa Vista Azul",
        "пляж Puntarena", "пляж Resonans Memoris Varadero",
        "пляж Roc Arenas Doradas", "пляж Roc Barlovento",
        "пляж Roc Varadero", "пляж Royalton Hicacos",
        "пляж Royalty Havana Paseo", "пляж Selectim Family Resort Varadero",
        "пляж Sirenis Tropical Varadero", "пляж Sol Caribe Beach",
        "пляж Sol Cayo Coco", "пляж Sol Palmeras", "пляж Sol Varadero",
        "пляж Starfish Cuatro Palmas", "пляж Starfish Varadero",
        "пляж Tryp Cayo Coco", "пляж Tuxpan Hotel",
        "пляж Valentin el Patriarca", "пляж Villa Cuba",
        "пляж Villa Tortuga", "пляж Woovo Playa Hermosa Cayo Paredon",
        "пляж Гаваны Санта Мария", "пляж Плайя Гирон", "пляж Анкон",
        "пляж Ранчо Луна", "пляж Аль Капоне", "пляж Плайя Пилар",
        "пляж Кайо Ларго", "пляж Кайо Бланко", "пляж Кайо Ромейро"
    ]
}

# Create database URL
url = f"postgresql://{params['user']}:{urllib.parse.quote_plus(params['password'])}@{params['host']}:{params['port']}/{params['database']}"

try:
    # Create engine
    engine = create_engine(url)
    
    with engine.connect() as conn:
        # Clear existing data
        conn.execute(text("DELETE FROM categories"))
        conn.commit()
        
        # Insert new data
        for category, items in categories_data.items():
            for item in items:
                conn.execute(
                    text("INSERT INTO categories (name, item_name) VALUES (:name, :item_name)"),
                    {"name": category, "item_name": item}
                )
        conn.commit()
        print("Данные успешно добавлены!")
        
except Exception as e:
    print(f"Ошибка: {e}") 