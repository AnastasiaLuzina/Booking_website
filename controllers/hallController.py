from flask import Blueprint, session, request, render_template, redirect, url_for
from tools.tools_for_base import connect_to_base, close_base
import sqlite3

hall_bp = Blueprint('hall', __name__)


class Halls_actions:
    

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






@hall_bp.route("/hall_update", methods=["POST"])
def add():
    title = request.form.get("title")
    address = request.form.get("address")
    description = request.form.get("description")
    
    errors = []
    Halls_actions.add_hall(title, address, description, errors)
        
    if not errors:
        # Перенаправляем на admin_page после успешного добавления
        return redirect(url_for('user.admin_page'))
    
    # При ошибке рендерим страницу с ошибками
    return render_template("authorization.html", errors=errors)


@hall_bp.route("/delete_hall", methods=["POST"])
def delete():
    hall_id = request.form.get("hall_id")
    errors = []
    Halls_actions.delete_hall(errors, hall_id)
    
    if not errors:
        return redirect(url_for('user.admin_page'))
    
    return render_template("admin_page.html", errors=errors)
   
   
           
@hall_bp.route("/hall", methods=["GET"])  # Убрано лишнее двоеточие
def get_hall():
    errors = [] 
    hall_id = request.args.get("hall_id")  # Исправлено на args для GET-запроса
    
    halls = Halls_actions.get_hall(errors, hall_id)  # Добавлен вызов через класс
    
    if not errors:
        return redirect(url_for("admin_page"))
    return render_template("admin_page.html", errors=errors)



@hall_bp.route("/hall/<int:hall_id>", methods=["POST"])
def edit(hall_id):
    title = request.form.get("title")
    address = request.form.get("address")
    description = request.form.get("description")
    
    errors = []
    Halls_actions.edit_hall(errors, hall_id, title, address, description)
    
    if not errors:
        return redirect(url_for('user.admin_page'))

    return render_template("admin_page.html", errors=errors)





    
# забыла вернуть return eroors
# забыла список error в каком то месте указать ;)              
# роутеры запускающиеся сжатия кнопок  
# роутеры организуют маршрутизацию, то есть при нажатии отправляется запрос и роутеры его ловят и выпоняют действия. В этом же случае это просто логика они никак не работают с html
# чтобы запустить и затестить нужно сразу связывать с html 
# в роутерах реализуется перенаправление и вызывается соотвествиющая логика/методы чтобы понять критикии по которым надо в то или иное место перенаправить пользователя

# чтобы удалять нужно не просто запррос в бд написать а принять request принять параметр по которому удаляем и потом перенаправляем на нужный html - без этого это просто метод, а не роутер (роутер на то и роутер чтоьы перенаправлять:)
# чтобы затестить нужно непосредственно это связать с html и их создать, чтобы собственно было взаимодейтсвие


















