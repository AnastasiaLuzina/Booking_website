import sqlite3
import hashlib

from controllers.userController import Checkers
import sys
sys.path.append('.')


connection = sqlite3.connect('booking_database.db')
cursor = connection.cursor()

# Удаление существующих таблиц
# cursor.execute("DROP TABLE IF EXISTS User")  
# cursor.execute("DROP TABLE IF EXISTS Hall") 
# cursor.execute("DROP TABLE IF EXISTS Booking")  
# cursor.execute("DROP TABLE IF EXISTS Photo")  # Исправлено Fhoto -> Photo
# cursor.execute("DROP TABLE IF EXISTS Equipment")  
# cursor.execute("DROP TABLE IF EXISTS CrossEquipmentHall")

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
    
    photo_bytes BLOB NOT NULL,
    hall_id INTEGER NOT NULL,
    FOREIGN KEY(hall_id) REFERENCES Hall(hall_id),
    
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Hall (
    hall_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    address TEXT NOT NULL,
    description TEXT NOT NULL,
    count_likes INTEGER NOT NULL
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


# Добавление администратора
hashed_password = Checkers.get_hash_password('1')  

cursor.execute('''
    INSERT INTO Equipment (title)
    VALUES (?)
''', ('Микрофоны',))
cursor.execute('''
    INSERT INTO Equipment (title)
    VALUES (?)
''', ('Зеркала',))
cursor.execute('''
    INSERT INTO Equipment (title)
    VALUES (?)
''', ('Колонки',))

# Добавление оборудования
equipment = [
    (1, 'Микрофоны'),
    (2, 'Зеркала'),
    (3, 'Колонки'),
    (4, 'Проектор'),
    (5, 'Световое оборудование'),
    (6, 'Сценические конструкции')
]
cursor.executemany('''
    INSERT INTO Equipment (equipment_id, title)
    VALUES (?, ?)
''', equipment)

# Добавление примеров залов с конкретными связями
halls = [
    (1, 'Бальный зал "Ренессанс"', 
     'ул. Центральная, 1', 
     'Просторный зал с высокими потолками и хрустальными люстрами', 
     15),
    
    (2, 'Конференц-зал "Бизнес"', 
     'пр. Ленина, 25', 
     'Современный зал для деловых встреч и конференций', 
     8),
    
    (3, 'Танцевальная студия "Грация"', 
     'ул. Творческая, 7', 
     'Профессиональная танцевальная студия с зеркальными стенами', 
     23)
]

cursor.executemany('''
    INSERT INTO Hall (hall_id, title, address, description, count_likes)
    VALUES (?, ?, ?, ?, ?)
''', halls)

# Создаем конкретные связи между залами и оборудованием
cross_links = [
    # Бальный зал (1) имеет микрофоны и колонки
    (1, 1), (3, 1),
    
    # Конференц-зал (2) имеет проектор и микрофоны
    (4, 2), (1, 2),
    
    # Танцевальная студия (3) имеет зеркала и световое оборудование
    (2, 3), (5, 3)
]

cursor.executemany('''
    INSERT INTO CrossEquipmentHall (equipment_id, hall_id)
    VALUES (?, ?)
''', cross_links)

# Фиксируем изменения и закрываем соединение
connection.commit()
connection.close()

print("База данных успешно инициализирована!")
print("Добавлено 3 зала с конкретным оборудованием:")
print("1. Бальный зал - Микрофоны, Колонки")
print("2. Конференц-зал - Проектор, Микрофоны")
print("3. Танцевальная студия - Зеркала, Световое оборудование")