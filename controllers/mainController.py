from flask import Blueprint, session, render_template, redirect, url_for
from controllers.hallController import Halls_actions  

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return redirect(url_for('user.authorization'))

@main_bp.route("/main_page")
def main_page():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    return render_template("main_page.html", user=session["user"])

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

@main_bp.route('/profile')
def profile():
    return render_template('profile.html')
    
    
