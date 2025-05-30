from flask import Blueprint, Flask, session, request, render_template, redirect, url_for
from tools.tools_for_base import connect_to_base, close_base, commit_in_base
import sqlite3

hall_bp = Blueprint('hall', __name__)

@hall_bp.route("/hall", methods=["GET"])#получение списка
def get_list_halls():
    try:
        conn, cursor = connect_to_base()
        cursor.execute("SELECT * FROM Hall")
        halls = cursor.fetchall()
        close_base(conn)
        return halls # наверное исправить
    except Exception as e:
        return render_template(
            "error.html",
            errors=[str(e)]
        )
    
@hall_bp.route("/hall/<int:hall_id>", methods=["GET"])#получение конкретного зала
def get_hall(hall_id):
    try:
        conn, cursor = connect_to_base()
        cursor.execute("SELECT title, address, description, count_likes FROM Hall WHERE hall_id = ?", (hall_id))
        hall = cursor.fetchall()
        close_base(conn)
        return hall # наверное исправить
    
    except Exception as e:
        return render_template(
            "error.html",
            errors=[str(e)]
        )
    
@hall_bp.route("/hall", mothods=["POST"])#добавление зала
def add_hall():
    try:
        title = request.form.get("title")
        address = request.form.get("address")
        description = request.form.get("description")
        conn, cursor = connect_to_base()
        cursor.execute(
                "INSERT INTO Hall (title, address, description, count_likes) VALUES (?, ?, ?, ?)",
                (title, address, description, 0))
        conn.commit()
        close_base(conn)
    except Exception as e:
        return render_template(
            "error.html",
            errors=[str(e)]
        )
    
@hall_bp.route("/hall/<int:hall_id>", methods=["PUT"])#редакирование зала
def edit_hall(hall_id):
    try:
        title = request.form.get("title")
        address = request.form.get("address")
        description = request.form.get("description")
        conn, cursor = connect_to_base()
        cursor.execute(
            "UPDATE Hall SET title = ?, type = ?, status = ? WHERE id = ?",
            (title, address, description, hall_id))
        conn.commit()
        close_base(conn)
    except Exception as e:
        return render_template(
            "error.html",
            errors=[str(e)]
        )
    
@hall_bp.route("/hall/<int:hall_id>", methods=["DELETE"])#удаление зала
def delete_hall(hall_id):
    try:
        conn, cursor = connect_to_base()
        cursor.execute("DELETE FROM Equipment WHERE id = ?", (hall_id,))
        conn.commit()
    except Exception as e:
        return render_template(
            "error.html",
            errors=[str(e)]
        )