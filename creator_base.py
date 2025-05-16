import sqlite3

connection = sqlite3.connect('my_database.db')
cursor = connection.cursor()

# Удаляем ВСЕ старые таблицы, которые могут мешать
cursor.execute("DROP TABLE IF EXISTS User")  # Удаляем старую таблицу с опечаткой
cursor.execute("DROP TABLE IF EXISTS Users")  # Пересоздаем Users с нуля
cursor.execute("DROP TABLE IF EXISTS Halls")  # Удаляем Halls, чтобы исправить adress → address
cursor.execute("DROP TABLE IF EXISTS Booking")  # Для согласованности

# Создаем таблицу Users (корректное имя)
cursor.execute('''
CREATE TABLE Users (
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

# Создаем таблицу Halls (исправляем adress → address)
cursor.execute('''
CREATE TABLE Halls (
    hall_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    address TEXT NOT NULL  
)
''')

# Создаем таблицу Booking
cursor.execute('''
CREATE TABLE Booking (
    booking_id INTEGER PRIMARY KEY,  
    user_id INTEGER NOT NULL,
    hall_id INTEGER NOT NULL,
    date TEXT,              
    start_time TEXT,
    end_time TEXT,
    status INTEGER,  
    FOREIGN KEY(user_id) REFERENCES Users(user_id),  
    FOREIGN KEY(hall_id) REFERENCES Halls(hall_id)
)
''')

connection.commit()
connection.close()