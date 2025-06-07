from flask import Blueprint, session, request, render_template, redirect, url_for, flash
from tools.tools_for_base import connect_to_base, close_base
import sqlite3
from controllers.userController import Checkers

profile_bp = Blueprint('profile', __name__)

class Profile_actions:
    
    @staticmethod
    def take_info(user_id):
        conn, cursor = connect_to_base()
        try:
            cursor.execute("""
                SELECT user_id, first_name, second_name, patronymic, 
                       login, email, age, flag_role
                FROM User 
                WHERE user_id = ?
            """, (user_id,))
            user_data = cursor.fetchone()
            return user_data
        finally:
            close_base(conn)

    @staticmethod
    def change_password(user_id, new_password, errors):
        if not Checkers.is_password_unique(new_password):
            errors.append("Этот пароль уже используется другим пользователем")
            return False
            
        try:
            hashed_password = Checkers.get_hash_password(new_password)
            conn, cursor = connect_to_base()
            cursor.execute("UPDATE User SET password = ? WHERE user_id = ?", (hashed_password, user_id))
            conn.commit()
            return True
        except:
            errors.append(f"Ошибка базы данных: {str(e)}")
            return False
        finally:
            close_base(conn)
            
    @staticmethod
    def change_email(user_id, new_email, errors):
        if not Checkers.is_email_unique(new_email):
            errors.append("Этот email уже используется другим пользователем")
        if not Checkers.is_valid_email(new_email):
            errors.append("Вы неверно ввели email")
            
        if errors:
            return False
            
        try:
            conn, cursor = connect_to_base()
            cursor.execute("UPDATE User SET email = ? WHERE user_id = ?", (new_email, user_id))
            conn.commit()
            return True
        except:
            errors.append(f"Ошибка базы данных: {str(e)}")
            return False
        finally:
            close_base(conn)
       
    @staticmethod
    def change_login(user_id, new_login, errors):
        if not Checkers.is_login_unique(new_login):
            errors.append("Этот логин уже занят")
            return False
            
        try:
            conn, cursor = connect_to_base()
            cursor.execute("UPDATE User SET login = ? WHERE user_id = ?", (new_login, user_id))
            conn.commit()
            return True
        except:
            errors.append(f"Ошибка базы данных: {str(e)}")
            return False
        finally:
            close_base(conn)
         
    @staticmethod
    def change_name(user_id, first_name, second_name, patronymic, errors):
        if not all([first_name, second_name, patronymic]):
            errors.append("Все поля должны быть заполнены")
            return False
            
        try:
            conn, cursor = connect_to_base()
            cursor.execute("""
                UPDATE User 
                SET first_name = ?, second_name = ?, patronymic = ? 
                WHERE user_id = ?
            """, (first_name, second_name, patronymic, user_id))
            conn.commit()
            return True
        except:
            errors.append(f"Ошибка базы данных: {str(e)}")
            return False
        finally:
            close_base(conn)






@profile_bp.route("/profile_password", methods=["POST"])
def password():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    errors = []
    user_id = session["user"]["id"]
    new_password = request.form.get("password")
    
    if Profile_actions.change_password(user_id, new_password, errors):
        flash("Пароль успешно изменен", "success")
    else:
    
        session['profile_errors'] = errors
    
    return redirect(url_for('profile.profile'))

@profile_bp.route("/profile_email", methods=["POST"])
def email():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    errors = []
    user_id = session["user"]["id"]
    new_email = request.form.get("email")
    
    if Profile_actions.change_email(user_id, new_email, errors):
        flash("Email успешно изменен", "success")
    else:
        session['profile_errors'] = errors
    
    return redirect(url_for('profile.profile'))

@profile_bp.route("/profile_login", methods=["POST"])
def login_change():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    errors = []
    user_id = session["user"]["id"]
    new_login = request.form.get("login")
    
    if Profile_actions.change_login(user_id, new_login, errors):
        flash("Логин успешно изменен", "success")
    else:
        session['profile_errors'] = errors
    
    return redirect(url_for('profile.profile'))

@profile_bp.route("/profile_name", methods=["POST"])
def name_change():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    errors = []
    user_id = session["user"]["id"]
    first_name = request.form.get("first_name")
    second_name = request.form.get("second_name")
    patronymic = request.form.get("patronymic")
    
    if Profile_actions.change_name(user_id, first_name, second_name, patronymic, errors):
        flash("Имя успешно изменено", "success")
    else:
        session['profile_errors'] = errors
    
    return redirect(url_for('profile.profile'))

@profile_bp.route('/profile')
def profile():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    # Получаем ошибки из сессии (если есть) и очищаем
    errors = session.pop('profile_errors', [])
    
    user_id = session["user"]["id"]
    user_data = Profile_actions.take_info(user_id)
    
    if not user_data:
        errors.append("Пользователь не найден")
        return render_template("profile.html", errors=errors)
        
    user_info = {
        "id": user_data[0],
        "first_name": user_data[1],
        "second_name": user_data[2],
        "patronymic": user_data[3],
        "login": user_data[4],
        "email": user_data[5],
        "age": user_data[6],
        "role": "Администратор" if user_data[7] == 1 else "Пользователь"
    }
        
    return render_template('profile.html', user=user_info, errors=errors)