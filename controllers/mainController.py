from flask import Blueprint, session, render_template, redirect, url_for
from controllers.hallController import Halls_actions  

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    user = session.get("user")
    return render_template("main.html", user=user)

@main_bp.route("/catalog_page")
def catalog_page():
    user = session.get("user")
    return render_template("catalog.html", user=user)

@main_bp.route("/about_page")
def about_page():  # Исправлено имя функции
    user = session.get("user")
    return render_template("about.html", user=user)

@main_bp.route("/admin_page")
def admin_page():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    user = session["user"]
    
    if user["role"] != 1:
        return redirect(url_for('main.main_page'))
    
    # Получаем список всех залов
    halls = Halls_actions.get_all_halls()
    
    return render_template("admin_page.html", user=user, halls=halls)


    
    
