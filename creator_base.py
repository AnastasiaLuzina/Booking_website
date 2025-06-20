import sqlite3
import hashlib
import os
from controllers.userController import Checkers
import sys
sys.path.append('.')

# Создаем папку для фото, если её нет
os.makedirs('static/photo', exist_ok=True)

connection = sqlite3.connect('booking_database.db')
cursor = connection.cursor()

# Удаление существующих таблиц
cursor.execute("DROP TABLE IF EXISTS User")  
cursor.execute("DROP TABLE IF EXISTS Hall") 
cursor.execute("DROP TABLE IF EXISTS Booking")  
cursor.execute("DROP TABLE IF EXISTS Photo")
cursor.execute("DROP TABLE IF EXISTS Equipment")  
cursor.execute("DROP TABLE IF EXISTS CrossEquipmentHall")

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    patronymic TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE, 
    email TEXT NOT NULL,
    age INTEGER,
    password TEXT NOT NULL,
    flag_role INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Equipment (
    equipment_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Photo (
    photo_id INTEGER PRIMARY KEY,
    hall_id INTEGER NOT NULL,
    photo_bytes BLOB NOT NULL,
    mime_type VARCHAR(50) NOT NULL DEFAULT 'image/jpeg',
    FOREIGN KEY(hall_id) REFERENCES Hall(hall_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Hall (
    hall_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    address TEXT NOT NULL,
    description TEXT NOT NULL  
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS CrossEquipmentHall (
    cross_equipment_hall_id INTEGER PRIMARY KEY,
    equipment_id INTEGER NOT NULL,
    hall_id INTEGER NOT NULL,
    FOREIGN KEY(hall_id) REFERENCES Hall(hall_id),
    FOREIGN KEY(equipment_id) REFERENCES Equipment(equipment_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Booking (
    booking_id INTEGER PRIMARY KEY,  
    user_id INTEGER NOT NULL,
    hall_id INTEGER NOT NULL,
    date TEXT NOT NULL,              
    start_time TEXT,
    end_time TEXT,
    status_for_admin INTEGER,  
    FOREIGN KEY(user_id) REFERENCES User(user_id),  
    FOREIGN KEY(hall_id) REFERENCES Hall(hall_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Likes (
    like_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    hall_id INTEGER NOT NULL,
    FOREIGN KEY(hall_id) REFERENCES Hall(hall_id),
    FOREIGN KEY(user_id) REFERENCES User(user_id)
)
''')

# Добавление администратора
hashed_password = Checkers.get_hash_password('1')  
cursor.execute('''
    INSERT INTO User (first_name, second_name, patronymic, login, email, age, password, flag_role)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('Админ', 'Админович', 'Админов', 'admin', 'admin@example.com', 30, hashed_password, 1))

# Добавление оборудования
equipment = [
    ('Микрофоны',),
    ('Зеркала',),
    ('Колонки',),
    ('Проектор',),
    ('Световое оборудование',),
    ('Сценические конструкции',)
]

cursor.executemany('''
    INSERT INTO Equipment (title)
    VALUES (?)
''', equipment)

# Добавление примеров залов
halls = [
    (1, 'Бальный зал "Ренессанс"', 
     'ул. Центральная, 1', 
     'Просторный зал с высокими потолками и хрустальными люстрами'),
    
    (2, 'Конференц-зал "Бизнес"', 
     'пр. Ленина, 25', 
     'Современный зал для деловых встреч и конференций'),
    
    (3, 'Танцевальная студия "Грация"', 
     'ул. Творческая, 7', 
     'Профессиональная танцевальная студия с зеркальными стенами')
]

cursor.executemany('''
    INSERT INTO Hall (hall_id, title, address, description)
    VALUES (?, ?, ?, ?)
''', halls)

# Связи между залами и оборудованием
cross_links = [
    (1, 1), (3, 1),  # Бальный зал (1)
    (4, 2), (1, 2),  # Конференц-зал (2)
    (2, 3), (5, 3)   # Танцевальная студия (3)
]

cursor.executemany('''
    INSERT INTO CrossEquipmentHall (equipment_id, hall_id)
    VALUES (?, ?)
''', cross_links)

# Функция для определения MIME-типа по расширению файла
def get_mime_type(filename):
    ext = filename.split('.')[-1].lower()
    if ext in ['jpg', 'jpeg']:
        return 'image/jpeg'
    elif ext == 'png':
        return 'image/png'
    elif ext == 'webp':
        return 'image/webp'
    else:
        return 'image/jpeg'  # по умолчанию

# Добавляем реальные изображения из папки static/photo
photo_files = [
    (1, 'ball_1.webp'),
    (1, 'ball_2.webp'),
    (2, 'ball_3.jpg'),
    (3, 'ball_4.webp')
]

for hall_id, filename in photo_files:
    filepath = os.path.join('static', 'photo', filename)
    try:
        with open(filepath, 'rb') as f:
            photo_bytes = f.read()
        mime_type = get_mime_type(filename)
        cursor.execute('''
            INSERT INTO Photo (hall_id, photo_bytes, mime_type)
            VALUES (?, ?, ?)
        ''', (hall_id, photo_bytes, mime_type))
    except FileNotFoundError:
        print(f"Файл {filepath} не найден, пропускаем...")
        continue

# Фиксируем изменения и закрываем соединение
connection.commit()
connection.close()
print("База данных успешно создана и заполнена тестовыми данными!")