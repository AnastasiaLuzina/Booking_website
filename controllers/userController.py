from flask import Flask, session, request, render_template, redirect, url_for, flash

import sqlite3
import re

from tools.tools_for_base import connect_to_base, close_base, commit_in_base
import hashlib


from flask import Blueprint

user_bp = Blueprint('user', __name__) 

class Checkers:
    
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
    def is_valid_login(login):
        # Добавляем проверку на None и пустую строку
        if not login or not login.strip():
            return False
        return len(login) >= 6
        
    # @staticmethod
    # def is_password_unique(password):
       
    #     hashed_password = Checkers.get_hash_password(password)
    #     conn, cursor = connect_to_base()
    #     cursor.execute("SELECT * FROM User WHERE password = ?", (hashed_password,))
    #     user = cursor.fetchone()
    #     close_base(conn)
    #     return user is None
    
    @staticmethod
    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_login_unique(login):
        # Исправлено: функция connect_to_base возвращает (conn, cursor)
        conn, cursor = connect_to_base()  # <-- Ранее было cursor = connect_to_base()
        cursor.execute("SELECT * FROM User WHERE login = ?", (login,))
        user = cursor.fetchone()
        close_base(conn)  # <-- Теперь передаем соединение для закрытия
        return user is None
        

    @staticmethod
    def get_hash_password(p: str) -> str:
         # Создаем MD5 хеш
        md5_hash = hashlib.md5()
        
        # Кодируем строку в байты (UTF-8) и обновляем хеш
        md5_hash.update(p.encode('utf-8'))
        
        # Получаем hex-представление хеша
        return md5_hash.hexdigest()
    

    @staticmethod
    def check_authorization(login, password):
        errors = []
        if not login or not password:
            flash("Необходимо заполниь все поля", "danger")
            errors = "Необходимо заполниь все поля"
        
        return errors

    @staticmethod
    def is_email_unique(email):
        # Исправлено: правильное управление соединением
        conn, cursor = connect_to_base()  # <-- 
        cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
        user = cursor.fetchone()
        close_base(conn)  # <-- 
        return user is None


    @staticmethod
    def check_registration(first_name, second_name, patronymic, login, email, age, password):
        errors = []
        if not all([first_name, second_name, patronymic, login, email, age, password]):
            flash("Заполните все поля", "danger")
            errors.append("Заполните все поля")
        else:

            try:
                age = int(age)
            except ValueError:
                errors.append("Возраст должен быть числом")
                flash("Возраст должен быть числом", "danger")
                age = 0 # Возвращаем ошибки сразу
            
            if not all(name.isalpha() for name in [first_name, second_name, patronymic]):
                errors.append("ФИО не должны содержать цифры или символы")
                flash("ФИО не должны содержать цифры или символы", "danger")
                
            elif not Checkers.is_valid_email(email):
                errors.append("Некорректный email")
                flash("Некорректный email", "danger")
                
            # elif not Checkers.is_login_unique(login):
            #     errors.append("Этот логин уже занят")
            
            # elif not Checkers.is_valid_login(login):
            #     errors.append("Логин должен быть длинее 6 символов")
                
            # elif not Checkers.is_password_unique(password):
            #     errors.append("Этот пароль уже используется другим пользователем")
                
            elif not Checkers.is_email_unique(email):
                errors.append("Этот email уже занят")
                flash("Этот email уже занят", "danger")
        return errors



    @staticmethod
    def admin_checker(user_id):
        cursor = connect_to_base()
        cursor.execute("SELECT flag_role FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        return user[0]
            


    
    
class Registration:    
    @staticmethod
    def add_to_base(first_name, second_name, patronymic, login, email, age, password, flag_role):
        # Исправлено: получаем и соединение, и курсор
        conn, cursor = connect_to_base()  # <-- 
        try:
            hashed_password = Checkers.get_hash_password(password)
            # Исправлено: указаны все столбцы таблицы (включая автоинкремент)
            cursor.execute('''
                INSERT INTO User (first_name, second_name, patronymic, login, email, age, password, flag_role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, second_name, patronymic, login, email, age, hashed_password, flag_role))
            user_id = cursor.lastrowid
            commit_in_base(conn)  # <-- Передаем соединение для коммита
            return True, user_id, flag_role
        except Exception as e:
            return False, str(e)
        finally:
            close_base(conn)  # <-- Закрываем соединение
                
class Authorization: 
    @staticmethod
    def comparison_to_base(login, password):
        try:
            
            conn, cursor = connect_to_base()
            
            cursor.execute("""
                                SELECT user_id, password, flag_role 
                                FROM User 
                                WHERE (email = ? OR login = ?) AND password = ?
                            """, (login, login, Checkers.get_hash_password(password)))
            
            user = cursor.fetchone()
            
            if not user:
                return (False, "Пользователь не найден")
            
            return (True, {
                'user_id': user[0],
                'flag_role': user[2]
            })
            
            
        except sqlite3.Error as e:
            return (False, None)
        finally:
            close_base(conn)


@user_bp.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        second_name = request.form.get("second_name")
        patronymic = request.form.get("patronymic")
        email = request.form.get("email")
        login = email.split('@')[0]
        age = request.form.get("age")
        password = request.form.get("password")
        flag_role = 0
       
        errors = Checkers.check_registration(first_name, second_name, patronymic, login, email, age, password)
        
        if not errors:
            result = Registration.add_to_base(first_name, second_name, patronymic, login, email, age, password, flag_role)
           
            if result[0]:
                    _, user_id, flag_role = result
                    session["id"] = user_id 
                    session["user"] = {"id": user_id, "email": email, "role": flag_role, "login": login}
                    return redirect(url_for('main.index'))  
            else:
                errors.append(result[1])
        return render_template("registration.html", errors=errors)
    return render_template("registration.html", errors=[])




@user_bp.route("/authorization", methods=["GET", "POST"])
def authorization():
    

    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        
        errors = Checkers.check_authorization(login, password) #проверка на пустоту полей
        
        if not errors:
            success, auth_data = Authorization.comparison_to_base(login, password)
            
            if success:
                session["id"] = auth_data['user_id']  
                session["user"] = {
                    "id": auth_data['user_id'],
                    "login": login,
                    "role": auth_data['flag_role'],
                    "email": login if '@' in login else ''  # Для совместимости
                }
                
                if auth_data['flag_role'] == 1:  # Проверка на админа
                     return redirect(url_for('main.admin_page'))
                
                # Получаем URL для перенаправления (из параметра ?next= или берём предыдущую страницу)
                next_url = request.args.get('next') or request.referrer
                
                # Проверяем, что next_url не ведёт на саму авторизацию (избегаем зацикливания)
                if next_url and url_for('user.authorization') not in next_url:
                    return redirect(next_url)
                else:
                    return redirect(url_for('main.index'))
            else:
                flash(auth_data, "danger")  # Добавляем сообщение об ошибке
                
        return render_template("authorization.html", errors=errors)
    return render_template("authorization.html", errors=[])

@user_bp.route("/edit_password", methods=["POST"])
def edit_password():
    password = request.form.get("password")
    errors = []
    if not password:
        errors.append("Заполните все поля")
        
    else:
        hashed_password = Checkers.get_hash_password(password)
        user_id = session["user"]["id"]
        user_data = Checkers.take_info(user_id)
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
        try:
            conn, cursor = connect_to_base()
            cursor.execute(
                "UPDATE User SET password = ? WHERE user_id = ?",  # Исправлены поля
                (hashed_password, user_id))
            conn.commit()
            close_base(conn)
            errors.append("Пароль успешно изменен!")
        except:
            errors.append("Ошибка с связью бд")
        
    return render_template('profile_edit.html', user = user_info,
                     js_alert=errors)
    
@user_bp.route("/edit_user", methods=["POST"])
def edit_user():
    first_name = request.form.get("first_name")
    second_name = request.form.get("second_name")
    patronymic = request.form.get("patronymic")
    email = request.form.get("email")
    age = request.form.get("age")
    
    if not all([first_name, second_name, patronymic, email, age]):
        flash("Заполните все обязательные поля", "danger")
        return redirect(url_for('profile.profile_edit_page'))
    
    try:
        user_id = session["user"]["id"]
        login = email.split('@')[0]
        conn, cursor = connect_to_base()
        cursor.execute("""
            UPDATE User SET first_name = ?, second_name = ?, patronymic = ?, email = ?, age = ?, login = ?
            WHERE user_id = ?""",
            (first_name, second_name, patronymic, email, age, login, user_id))
        conn.commit()
        flash("Изменения успешно сохранены!", "success")
    except Exception as e:
        print(f"Database error: {str(e)}")
        flash("Ошибка при сохранении изменений", "danger")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): close_base(conn)
    
    return redirect(url_for('profile.profile_edit_page'))
    
    

@user_bp.route("/login")
def login():
    if "user" in session:
        return render_template("authorization.html")
    return redirect(url_for('user.authorization'))

@user_bp.route("/authorization_verification")
def authorization_verification():
    if "user" not in session:
        return 0
    return 1


@user_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('user.authorization'))