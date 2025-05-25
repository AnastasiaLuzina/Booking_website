
import sqlite3

DATABASE = 'booking_database.db'

def connect_to_base():
    conn = sqlite3.connect(DATABASE)
    return conn, conn.cursor()  # Возвращаем и соединение, и курсор

def close_base(conn):
    if conn:
        conn.close()  # Закрываем соединение

def commit_in_base(conn):
    if conn:
        try:
            conn.commit()
        except Exception as e:
            print(f"Ошибка при коммите: {e}")
