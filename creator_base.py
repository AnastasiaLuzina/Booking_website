import sqlite3

connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
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
CREATE TABLE IF NOT EXISTS Halls (
    hall_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    adress TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Booking (
    booking_id INTEGER PRIMARY KEY,  
    user_id INTEGER NOT NULL,
    hall_id INTEGER NOT NULL,
    date TEXT,              
    start_time TEXT,
    end_time TEXT,
    status INTEGER,  -- Запятая здесь важна!
    FOREIGN KEY(user_id) REFERENCES Users(user_id),  
    FOREIGN KEY(hall_id) REFERENCES Halls(hall_id)
)
''')

connection.commit()
connection.close()
