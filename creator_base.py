import sqlite3
import hashlib
from controllers.userController import Checkers

connection = sqlite3.connect('booking_database.db')
cursor = connection.cursor()


# cursor.execute("DROP TABLE IF EXISTS User")  
# cursor.execute("DROP TABLE IF EXISTS Hall") 
# cursor.execute("DROP TABLE IF EXISTS Booking")  
# cursor.execute("DROP TABLE IF EXISTS Fhoto") 
# cursor.execute("DROP TABLE IF EXISTS Equipment")  
# cursor.execute("DROP TABLE IF EXISTS CrossEquipmentHall")





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
CREATE TABLE IF NOT EXISTS Fhoto (
    equipment_id INTEGER PRIMARY KEY,
    fhoto_bytes BLOB NOT NULL,
    hall_id INTRGER NOT NULL,
    FOREIGN KEY(hall_id) REFERENCES Hall(hall_id)
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
CREATE TABLE IF NOT EXISTS CrossEquipmentHalls (
        crossEquipmentHalls_id INTEGER PRIMARY KEY,
        equipment_id INTRGER NOT NULL,
        hall_id INTRGER NOT NULL,
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


hashed_password = Checkers.get_hash_password('1')  
cursor.execute('''
    INSERT INTO User (first_name, second_name, patronymic, login, email, age, password, flag_role)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('Вася', 'Пупкин', 'Пуповинович', 'admin', 'admin@example.com', 99, hashed_password, 1))

connection.commit()
connection.close()
