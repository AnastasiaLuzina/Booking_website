
from flask import Blueprint, session, request, render_template, redirect, url_for
from tools.tools_for_base import connect_to_base, close_base
import base64  # Добавьте эту строку
import sqlite3



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
        conn, cursor = connect_to_base()
        cursor.execute('''
            SELECT h.hall_id, h.title, p.photo_bytes 
            FROM Hall h
            LEFT JOIN Photo p ON h.hall_id = p.hall_id
            ORDER BY h.hall_id, p.photo_id
        ''')
        halls_data = cursor.fetchall()
        close_base(conn)
        
        return [{
            'hall_id': hall_id,
            'title': title,
            'photo': base64.b64encode(photo_bytes).decode('utf-8') if photo_bytes else None
        } for hall_id, title, photo_bytes in halls_data]
        
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



@hall_bp.route("/hall_add", methods=["GET"])
def add_form():
    return render_template("add_hall.html")


@hall_bp.route("/hall_update", methods=["POST"])
def add():
    title = request.form.get("title")
    address = request.form.get("address")
    description = request.form.get("description")
    errors = []
    
    if not title or not address:
        errors.append("Название и адрес обязательны")
    else:
        Halls_actions.add_hall(title, address, description, errors)
    
    if not errors:
        return redirect(url_for('main.admin_page'))
    return render_template("add_hall.html", errors=errors, title=title, address=address, description=description)


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
    
    if hall:
        # Получаем фотографии зала
        conn, cursor = connect_to_base()
        cursor.execute("SELECT photo_id FROM Photo WHERE hall_id = ?", (hall_id,))
        photos = cursor.fetchall()
        close_base(conn)
        
        # Получаем оборудование зала
        equipment_list = Halls_actions.get_equipment_for_hall(hall_id)
        
        return render_template("hall_detail.html", 
                              hall=hall, 
                              photos=photos,
                              equipment_list=equipment_list)
    
    errors.append("Зал не найден")
    return render_template("admin_page.html", errors=errors)


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





    
# забыла вернуть return eroors
# забыла список error в каком то месте указать ;)              
# роутеры запускающиеся сжатия кнопок  
# роутеры организуют маршрутизацию, то есть при нажатии отправляется запрос и роутеры его ловят и выпоняют действия. В этом же случае это просто логика они никак не работают с html
# чтобы запустить и затестить нужно сразу связывать с html 
# в роутерах реализуется перенаправление и вызывается соотвествиющая логика/методы чтобы понять критикии по которым надо в то или иное место перенаправить пользователя

# чтобы удалять нужно не просто запррос в бд написать а принять request принять параметр по которому удаляем и потом перенаправляем на нужный html - без этого это просто метод, а не роутер (роутер на то и роутер чтоьы перенаправлять:)
# чтобы затестить нужно непосредственно это связать с html и их создать, чтобы собственно было взаимодейтсвие



















