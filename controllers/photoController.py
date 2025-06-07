from flask import Blueprint, Response, send_file, render_template
from tools.tools_for_base import connect_to_base, close_base
import os
import sqlite3  # Добавьте эту строку

photo_bp = Blueprint('photo', __name__)

class PhotoService:
    @staticmethod
    def get_first_photo_by_hall(hall_id):
        """Получает первую фотографию для указанного зала"""
        conn, cursor = None, None
        try:
            conn, cursor = connect_to_base()
            cursor.execute("""
                SELECT photo_bytes, mime_type 
                FROM Photo 
                WHERE hall_id = ?
                ORDER BY photo_id
                LIMIT 1
            """, (hall_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Ошибка при получении фото: {e}")
            return None
        finally:
            if conn:
                close_base(conn)
    
    @staticmethod
    def get_all_halls_with_photos():
        """Получает все залы с информацией о наличии фото"""
        conn, cursor = None, None
        try:
            conn, cursor = connect_to_base()
            # ИСПРАВЛЕННЫЙ ЗАПРОС: добавлен префикс h. к hall_id
            cursor.execute("""
                SELECT h.hall_id, h.title, h.address, h.description, h.count_likes,
                       (SELECT COUNT(*) FROM Photo WHERE hall_id = h.hall_id) AS photo_count
                FROM Hall h
            """)
            halls = cursor.fetchall()
            
            hall_list = []
            for hall in halls:
                hall_dict = {
                    'hall_id': hall[0],
                    'title': hall[1],
                    'address': hall[2],
                    'description': hall[3],
                    'count_likes': hall[4],
                    'has_photo': hall[5] > 0
                }
                hall_list.append(hall_dict)
            return hall_list
        except Exception as e:
            print(f"Ошибка при получении залов: {e}")
            return []
        finally:
            if conn:
                close_base(conn)

@photo_bp.route('/photo/<int:photo_id>')
def get_photo(photo_id):
    conn = sqlite3.connect('booking_database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT photo_bytes, mime_type FROM Photo WHERE photo_id = ?', (photo_id,))
    photo = cursor.fetchone()
    conn.close()
    
    if photo:
        return Response(photo[0], mimetype=photo[1])
    else:
        return "Photo not found", 404
    
@photo_bp.route('/halls')
def halls():
    conn = sqlite3.connect('booking_database.db')
    cursor = conn.cursor()
    
    # Получаем залы с их первым фото
    cursor.execute('''
        SELECT h.*, p.photo_id 
        FROM Hall h
        LEFT JOIN Photo p ON p.hall_id = h.hall_id
        GROUP BY h.hall_id
    ''')
    halls = cursor.fetchall()
    conn.close()
    
    return render_template('halls.html', halls=halls)