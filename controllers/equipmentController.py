from flask import Blueprint, session, request, render_template, redirect, url_for
from tools.tools_for_base import connect_to_base, close_base
import sqlite3

equipment_bp = Blueprint('equipment', __name__)


class EquipmentActions:
    
    @staticmethod
    def get_equipment(equipment_id):
        try:
            conn, cursor = connect_to_base()
            cursor.execute("SELECT * FROM Equipment WHERE equipment_id = ?", (equipment_id,))
            equipment = cursor.fetchone()
            close_base(conn)
            return equipment
        except:
            return None
    
    @staticmethod
    def get_all_equipment_for_hall(hall_id):
        try:
            conn, cursor = connect_to_base()
            cursor.execute("SELECT * FROM Equipment WHERE hall_id = ?", (hall_id,))
            equipment_list = cursor.fetchall()
            close_base(conn)
            return equipment_list
        except:
            return []



@equipment_bp.route("/hall_equipment", methods=["GET"])
def view_equipment():
    hall_id = request.args.get("hall_id")  # Получаем ID зала из URL-параметра
    equipment_list = EquipmentActions.get_all_equipment_for_hall(hall_id)
    errors = []
    
    if equipment_list:
        return render_template("hall_equipment.html", 
                              equipment_list=equipment_list, 
                              hall_id=hall_id)
    
    errors.append("Оборудование для зала не найдено")
    return render_template("admin_page.html", errors=errors)


# Роут для формы добавления оборудования
@equipment_bp.route("/equipment_add", methods=["GET"])
def add_form():
    hall_id = request.args.get("hall_id")
    return render_template("add_equipment.html", hall_id=hall_id)


# Роут для добавления оборудования
@equipment_bp.route("/equipment_add", methods=["POST"])
def add():
    hall_id = request.form.get("hall_id")
    name = request.form.get("name")
    count = request.form.get("count")
    description = request.form.get("description")
    errors = []
    
    if not name or not count:
        errors.append("Название и количество обязательны")
    else:
        EquipmentActions.add_equipment(hall_id, name, count, description, errors)
    
    if not errors:
        return redirect(url_for('equipment.view_equipment', hall_id=hall_id))
    return render_template("add_equipment.html", 
                          errors=errors, 
                          hall_id=hall_id,
                          name=name,
                          count=count,
                          description=description)


# Роут для удаления оборудования
@equipment_bp.route("/delete_equipment", methods=["POST"])
def delete():
    equipment_id = request.form.get("equipment_id")
    hall_id = request.form.get("hall_id")
    errors = []
    EquipmentActions.delete_equipment(errors, equipment_id)
    
    if not errors:
        return redirect(url_for('equipment.view_equipment', hall_id=hall_id))
    
    return render_template("hall_equipment.html", 
                         errors=errors, 
                         hall_id=hall_id,
                         equipment_list=EquipmentActions.get_all_equipment_for_hall(hall_id))


# Роут для формы редактирования оборудования
@equipment_bp.route("/equipment_edit/<int:equipment_id>", methods=["GET"])
def edit_form(equipment_id):
    equipment = EquipmentActions.get_equipment(equipment_id)
    if equipment:
        return render_template("edit_equipment.html", equipment=equipment)
    return redirect(url_for('main.admin_page'))


# Роут для сохранения изменений оборудования
@equipment_bp.route("/equipment_edit/<int:equipment_id>", methods=["POST"])
def edit(equipment_id):
    name = request.form.get("name")
    count = request.form.get("count")
    description = request.form.get("description")
    hall_id = request.form.get("hall_id")
    
    errors = []
    EquipmentActions.edit_equipment(errors, equipment_id, name, count, description)
    
    if not errors:
        return redirect(url_for('equipment.view_equipment', hall_id=hall_id))

    equipment = EquipmentActions.get_equipment(equipment_id)
    return render_template("edit_equipment.html", 
                          equipment=equipment, 
                          errors=errors)
    
@equipment_bp.route("/all_equipment", methods=["GET"])
def view_all_equipment():
    try:
        conn, cursor = connect_to_base()
        cursor.execute("""
            SELECT e.equipment_id, e.name, e.count, e.description, h.title
            FROM Equipment e
            JOIN Hall h ON e.hall_id = h.hall_id
        """)
        all_equipment = cursor.fetchall()
        close_base(conn)
        return render_template("all_equipment.html", equipment_list=all_equipment)
    except Exception as e:
        # Получаем необходимые данные для admin_page.html
        from controllers.mainController import Halls_actions
        halls = Halls_actions.get_all_halls()
        user_info = session.get("user", {})
        
        return render_template("admin_page.html", 
                              errors=[f"Ошибка при загрузке оборудования: {str(e)}"],
                              halls=halls,
                              user=user_info)