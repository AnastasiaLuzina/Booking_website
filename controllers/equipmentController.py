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


# Роут для просмотра оборудования в зале
@equipment_bp.route("/hall_equipment", methods=["GET"])
def view_equipment():
    hall_id = request.args.get("hall_id")  # Получаем ID зала из URL-параметра
    equipment_list = EquipmentActions.get_all_equipment_for_hall(hall_id)
    
    if equipment_list:
        return render_template("hall_equipment.html", 
                              equipment_list=equipment_list, 
                              hall_id=hall_id)
    
    # Если оборудование не найдено
    return render_template("admin_page.html", errors=["Оборудование для зала не найдено"])