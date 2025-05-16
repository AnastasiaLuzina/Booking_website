import sqlite3

connection = sqlite3.connect('booking_halls_database.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    patronymic TEXT NOT NULL,
    email TEXT NOT NULL,
    age INTEGER,
    password TEXT,
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
    adress TEXT NOT NULL,
    description TEXT NOT NULL,
    equipment_id INTEGER NOT NULL,
    count_likes INTEGER NOT NULL,
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
    status_for_admin INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES User(user_id),  
    FOREIGN KEY(hall_id) REFERENCES Hall(hall_id)
)
''')

connection.commit()
connection.close()
