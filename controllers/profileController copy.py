from flask import Blueprint, session, request, render_template, redirect, url_for
from tools.tools_for_base import connect_to_base, close_base
import sqlite3

profile_bp = Blueprint('profile', __name__)

class Profile_actions:
    
    def change_password():
        try:
            conn, cursor = connect_to_base()
                cursor.execute("DELETE FROM Hall WHERE hall_id = ?", (hall_id,))  # Исправлена таблица и параметр
                conn.commit()
                close_base(conn)  
        except:
            errors.append("Ошибка с связью бд")
        
    

@profile_bp.route("/profile_password", methods=["GET"])
def password():
    

@profile_bp.route("/profile_email", methods=["GET"])
def email():
    

@profile_bp.route("/profile_login", methods=["GET"])
def login():
    

@profile_bp.route("/profile_name", methods=["GET"])
def name():
    