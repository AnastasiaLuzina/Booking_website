import sqlite3

DATABASE = 'booking_database.db'

def connect_to_base():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        return cursor
    except Exception as e:
            return (print(e))

def close_base():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.close()
    except Exception as e:
            return (print(e))

def commit_in_base():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.commit()
    except Exception as e:
        return (print(e))