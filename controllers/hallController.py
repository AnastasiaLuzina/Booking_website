
from flask import Blueprint, session, request, render_template, redirect, url_for, jsonify
from tools.tools_for_base import connect_to_base, close_base
import base64  # Добавьте эту строку
import sqlite3
from functools import wraps


hall_bp = Blueprint('hall', __name__)

    
class Halls_actions:
    
    
    @staticmethod
    def get_hall_by_id(hall_id):
        """Получает зал по ID"""
        try:
            conn, cursor = connect_to_base()
            cursor.execute("SELECT * FROM Hall WHERE hall_id = ?", (hall_id,))
            hall = cursor.fetchone()
            close_base(conn)
            return hall
        except Exception as e:
            print(f"Error getting hall: {str(e)}")
            return None
        
    
    @staticmethod
    def get_halls_with_photos():
        try:
            conn, cursor = connect_to_base()
            cursor.execute('''
                SELECT h.hall_id, h.title, 
                    (SELECT p.photo_bytes FROM Photo p 
                        WHERE p.hall_id = h.hall_id 
                        ORDER BY p.photo_id LIMIT 1) as cover_photo
                FROM Hall h
                ORDER BY h.title
            ''')
            halls_data = cursor.fetchall()
            close_base(conn)
            
            return [{
                'hall_id': hall_id,
                'title': title,
                'photo': base64.b64encode(photo_bytes).decode('utf-8') if photo_bytes else None
            } for hall_id, title, photo_bytes in halls_data]
        except:
            return None
        
    @staticmethod
    def get_hall_full(hall_id):
        try:
            conn, cursor = connect_to_base()
            cursor.execute("SELECT * FROM Hall WHERE hall_id = ?", (hall_id,))
            hall = cursor.fetchone()
            close_base(conn)
            return hall
        except:
            return None
    
    @staticmethod
    def get_hall(hall_id):
        try:
            conn, cursor = connect_to_base()
            cursor.execute("SELECT * FROM Hall WHERE hall_id = ?", (hall_id,))
            hall = cursor.fetchone()
            close_base(conn)
            return hall
        except:
            return None
        
    @staticmethod
    def get_equipment_for_hall(hall_id):
        try:
            conn, cursor = connect_to_base()
            cursor.execute("""
                SELECT e.title 
                FROM Equipment e
                JOIN CrossEquipmentHall ceh ON e.equipment_id = ceh.equipment_id
                WHERE ceh.hall_id = ?
            """, (hall_id,))
            equipment = cursor.fetchall()
            close_base(conn)
            return equipment
        except:
            return []
        

    @staticmethod
    def get_all_halls():
        try:
            conn, cursor = connect_to_base()
            cursor.execute("SELECT hall_id, title, address FROM Hall")
            halls = cursor.fetchall()
            close_base(conn)
            return halls
        except Exception as e:
            return []
    
    
    @staticmethod    
    def delete_hall(errors, hall_id):  # Добавлен параметр errors
        try:
            conn, cursor = connect_to_base()
            cursor.execute("DELETE FROM Hall WHERE hall_id = ?", (hall_id,))  # Исправлена таблица и параметр
            conn.commit()
            close_base(conn)  # Добавлено закрытие соединения
        except:
            errors.append("Ошибка с связью бд")
            
            
            
            
    @staticmethod           
    def edit_hall(errors, hall_id, title, address, description):  # Добавлены параметры
        try:
            conn, cursor = connect_to_base()
            cursor.execute(
                "UPDATE Hall SET title = ?, address = ?, description = ? WHERE hall_id = ?",  # Исправлены поля
                (title, address, description, hall_id))
            conn.commit()
            close_base(conn)
        except:
            errors.append("Ошибка с связью бд")
            
            
            
            
    @staticmethod   
    def add_hall(title, address, description, errors):
        try:
            conn, cursor = connect_to_base()  # Добавлено получение соединения
            cursor.execute(
                    "INSERT INTO Hall (title, address, description, count_likes) VALUES (?, ?, ?, ?)",
                    (title, address, description, 0))
            conn.commit()
            close_base(conn)
        except:
            errors.append("Ошибка с связью бд")
        return errors
    
    @staticmethod
    def search_like(hall_id, user_id, errors):
        try:
            conn, cursor = connect_to_base()  # Добавлено получение соединения
            cursor.execute(
                    "SELECT * FROM Likes WHERE user_id = ? AND hall_id = ?",
                    (user_id, hall_id))
            
            likes = cursor.fetchone()
            close_base(conn)
            return likes
        except:
            errors.append("Ошибка с связью бд")
        
    @staticmethod
    def get_top_three_halls():
        try:
            conn, cursor = connect_to_base()
            cursor.execute("""
                SELECT 
                    h.hall_id,
                    h.title,
                    h.address,
                    h.description,
                    (SELECT COUNT(*) FROM Likes l WHERE l.hall_id = h.hall_id) AS likes_count,
                    (SELECT p.photo_bytes FROM Photo p WHERE p.hall_id = h.hall_id LIMIT 1) AS photo,
                    COUNT(b.booking_id) AS booking_count
                FROM Hall h
                LEFT JOIN Booking b ON h.hall_id = b.hall_id 
                    AND strftime('%Y-%m', b.date) = strftime('%Y-%m', 'now')
                    
                GROUP BY h.hall_id, h.title, h.address, h.description
                ORDER BY booking_count DESC
                LIMIT 3
            """)
            
            top_halls = []
            for row in cursor.fetchall():
                top_halls.append({
                    'hall_id': row[0],
                    'title': row[1],
                    'address': row[2],
                    'description': row[3],
                    'likes_count': row[4],
                    'photo': base64.b64encode(row[5]).decode('utf-8') if row[5] else None,
                    'booking_count': row[6]  # Добавляем количество бронирований
                })
            
            return top_halls
        except Exception as e:
            print(f"Error getting top halls by bookings: {str(e)}")
            return []
        
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): close_base(conn)
    

    @staticmethod
    def get_liked_halls(user_id):
        try:
            conn, cursor = connect_to_base()
            cursor.execute("""
                SELECT 
                    h.hall_id,
                    h.title,
                    (SELECT p.photo_bytes FROM Photo p WHERE p.hall_id = h.hall_id LIMIT 1) AS photo
                FROM Hall h
                JOIN Likes l ON h.hall_id = l.hall_id
                WHERE l.user_id = ?
                ORDER BY h.title
            """, (user_id,))
            
            liked_halls = []
            for row in cursor.fetchall():
                liked_halls.append({
                    'hall_id': row[0],
                    'title': row[1],
                    'photo': base64.b64encode(row[2]).decode('utf-8') if row[2] else None
                })
            
            return liked_halls
        except Exception as e:
            print(f"Error getting user liked halls: {str(e)}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): close_base(conn)

    @staticmethod
    def add_hall_with_photos(title, address, description, photos):
        try:
            conn, cursor = connect_to_base()
            cursor.execute(
                "INSERT INTO Hall (title, address, description) VALUES (?, ?, ?)",
                (title, address, description))
            hall_id = cursor.lastrowid
            
            # Сохраняем фотографии
            for photo in photos:
                if photo.filename != '':
                    photo_bytes = photo.read()
                    mime_type = photo.mimetype
                    cursor.execute(
                        "INSERT INTO Photo (hall_id, photo_bytes, mime_type) VALUES (?, ?, ?)",
                        (hall_id, photo_bytes, mime_type))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding hall: {str(e)}")
            return False
        finally:
            close_base(conn)
    
    @staticmethod
    def update_hall(hall_id, title, address, description, new_photos):
        try:
            conn, cursor = connect_to_base()
            cursor.execute(
                "UPDATE Hall SET title = ?, address = ?, description = ? WHERE hall_id = ?",
                (title, address, description, hall_id))
            
            # Добавляем новые фото
            for photo in new_photos:
                if photo.filename != '':
                    photo_bytes = photo.read()
                    mime_type = photo.mimetype
                    cursor.execute(
                        "INSERT INTO Photo (hall_id, photo_bytes, mime_type) VALUES (?, ?, ?)",
                        (hall_id, photo_bytes, mime_type))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating hall: {str(e)}")
            return False
        finally:
            close_base(conn)




@hall_bp.route("/hall_add", methods=["POST"])
def add_hall():
    title = request.form.get("title")
    address = request.form.get("address")
    description = request.form.get("description")
    photos = request.files.getlist("photos")
    
    if Halls_actions.add_hall_with_photos(title, address, description, photos):
        flash("Зал успешно добавлен", "success")
    else:
        flash("Ошибка при добавлении зала", "danger")
    
    return redirect(url_for('main.admin_page'))

@hall_bp.route("/hall_update", methods=["POST"])
def update_hall():
    hall_id = request.form.get("hall_id")
    title = request.form.get("title")
    address = request.form.get("address")
    description = request.form.get("description")
    new_photos = request.files.getlist("new_photos")
    
    if Halls_actions.update_hall(hall_id, title, address, description, new_photos):
        flash("Зал успешно обновлен", "success")
    else:
        flash("Ошибка при обновлении зала", "danger")
    
    return redirect(url_for('main.admin_page'))


@hall_bp.route("/delete_hall", methods=["POST"])
def delete():
    hall_id = request.form.get("hall_id")
    errors = []
    Halls_actions.delete_hall(errors, hall_id)
    
    if not errors:
        return redirect(url_for('main.admin_page'))
    
    return render_template("admin_page.html", errors=errors)
   
   
           
@hall_bp.route("/hall", methods=["GET"])
def get_hall():
    errors = []
    hall_id = request.args.get("hall_id")
    hall = Halls_actions.get_hall(hall_id)
    user = session.get("user", None)
    user_id = session.get("id", None)   
    
    # Добавляем проверку лайка пользователя
    user_has_liked = False
    if user and 'id' in user:
        try:
            conn, cursor = connect_to_base()
            cursor.execute(
                "SELECT 1 FROM Likes WHERE user_id = ? AND hall_id = ?",
                (user['id'], hall_id)
            )
            user_has_liked = cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking like: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): close_base(conn)

    if hall:
        conn, cursor = connect_to_base()
        cursor.execute("SELECT photo_id FROM Photo WHERE hall_id = ?", (hall_id,))
        photos = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM Likes WHERE hall_id = ?", (hall_id,))
        total_likes = cursor.fetchone()[0]
        close_base(conn)
        
        equipment_list = Halls_actions.get_equipment_for_hall(hall_id)
        
        return render_template("hall_detail.html", 
                            hall=hall, 
                            photos=photos,
                            equipment_list=equipment_list,
                            total_likes=total_likes,
                            user=user,
                            user_has_liked=user_has_liked)  # Добавляем этот параметр
    
    errors.append("Зал не найден")
    return render_template("admin_page.html", errors=errors)

@hall_bp.route("/check_auth", methods=["GET"])
def check_auth():
    return jsonify({
    'authenticated': 'user' in session,
    'user_id': session.get('id')
})

@hall_bp.route("/hall_edit/<int:hall_id>", methods=["GET"])
def edit_form(hall_id):
    hall = Halls_actions.get_hall(hall_id)
    if hall:
        return render_template("edit_form.html", hall=hall)
    return redirect(url_for('main.admin_page'))


@hall_bp.route("/hall_edit/<int:hall_id>", methods=["POST"])
def edit(hall_id):
    title = request.form.get("title")
    address = request.form.get("address")
    description = request.form.get("description")
    
    errors = []
    Halls_actions.edit_hall(errors, hall_id, title, address, description)
    
    if not errors:
        return redirect(url_for('main.admin_page'))

    return render_template("admin_page.html", errors=errors)

@hall_bp.route("/hall_likes/<int:hall_id>", methods=['POST'])

def hall_likes(hall_id):
    if 'user' not in session:
        return jsonify({'error': 'Not authorized'}), 401
    user_id = session['user']['id']

    try:
        conn, cursor = connect_to_base()
        
        # Проверяем существование лайка
        cursor.execute("SELECT 1 FROM Likes WHERE user_id = ? AND hall_id = ?", (user_id, hall_id))
        existing_like = cursor.fetchone()
        
        if existing_like:
            cursor.execute("DELETE FROM Likes WHERE user_id = ? AND hall_id = ?", (user_id, hall_id))
            action = 'unliked'
        else:
            cursor.execute("INSERT INTO Likes (user_id, hall_id) VALUES (?, ?)", (user_id, hall_id))
            action = 'liked'
        
        cursor.execute("SELECT COUNT(*) FROM Likes WHERE hall_id = ?", (hall_id,))
        likes_count = cursor.fetchone()[0]
        
        conn.commit()
        
        return jsonify({
            'status': 'success',
            'action': action,
            'likes_count': likes_count
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): close_base(conn)




    
# забыла вернуть return eroors
# забыла список error в каком то месте указать ;)              
# роутеры запускающиеся сжатия кнопок  
# роутеры организуют маршрутизацию, то есть при нажатии отправляется запрос и роутеры его ловят и выпоняют действия. В этом же случае это просто логика они никак не работают с html
# чтобы запустить и затестить нужно сразу связывать с html 
# в роутерах реализуется перенаправление и вызывается соотвествиющая логика/методы чтобы понять критикии по которым надо в то или иное место перенаправить пользователя

# чтобы удалять нужно не просто запррос в бд написать а принять request принять параметр по которому удаляем и потом перенаправляем на нужный html - без этого это просто метод, а не роутер (роутер на то и роутер чтоьы перенаправлять:)
# чтобы затестить нужно непосредственно это связать с html и их создать, чтобы собственно было взаимодейтсвие



















