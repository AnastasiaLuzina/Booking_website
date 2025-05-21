from flask import Flask, session, request, render_template, redirect, url_for

import sqlite3
import re

import hashlib
import secrets

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

DATABASE = 'booking_database.db'

class Checkers:
    
    def is_valid_login(login):
        if len(login) < 6:
            return False
        return True
        
    @staticmethod
    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_login_unique(login):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE login = ?", (login,))
        user = cursor.fetchone()
        conn.close()
        return user is None
        
        

    @staticmethod
    def hash_password(password, salt=None):
        if salt is None:
            salt = secrets.token_hex(16)  
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"  
    
    @staticmethod
    def check_hashed_password(password, stored_hash):
        salt, hashed = stored_hash.split('$')
        new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return new_hash == hashed

    @staticmethod
    def is_email_unique(email):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user is None


    @staticmethod
    def check_registration(first_name, second_name, patronymic, login, email, age, password):
        errors = []
        if not all([first_name, second_name, patronymic, email, age, password]):
            errors.append("Заполните все поля")
        else:
            if not all(name.isalpha() for name in [first_name, second_name, patronymic]):
                errors.append("ФИО не должны содержать цифры или символы")
 
            if not 18 <= age <= 100:
                errors.append("Возраст должен быть от 18 до 100 лет")
                
            elif not isinstance(age, int):
                errors.append("Возраст должен быть числом")
                
            elif not Checkers.is_valid_email(email):
                errors.append("Некорректный email")
                
            elif not Checkers.is_login_unique(login):
                errors.append("Этот логин уже занят")
            
            elif not Checkers.is_valid_login(login):
                errors.append("Логин должен быть длинее 6 символов")
                
            elif not Checkers.is_email_unique(email):
                errors.append("Этот email уже занят")
        return errors

    @staticmethod
    def check_authorization(login, password):
        errors = []
        if not login or not password:
            errors.append("Заполните все поля")
        else:
            
            if Checkers.is_login_unique(login):
                errors.append("Пользователь с таким логином не найден")
                
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE login = ?", (login,))
            user = cursor.fetchone()
            conn.close()
            if not user:
                errors.append("Пользователь не найден")
            else:
                if not Checkers.check_hashed_password(password, user[5]):
                    errors.append("Неверный пароль")
        return errors

    @staticmethod
    def admin_checker(user_id):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT flag_role FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        return user[0]
            


    
    
class Registration:    
    @staticmethod
    def add_to_base(first_name, second_name, patronymic, login, email, age, password, flag_role):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            hashed_password = Checkers.hash_password(password)
            cursor.execute('''
                INSERT INTO User (first_name, second_name, patronymic, login, email, age, password, flag_role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, second_name, patronymic, login, email, age, hashed_password, flag_role))
            user_id = cursor.lastrowid
            conn.commit()
            return True, user_id, flag_role
        except sqlite3.IntegrityError as e:
            return False, f"Ошибка: {e}"
        except Exception as e:
            return False, f"Произошла ошибка: {e}"
        finally:
            conn.close()
                
                
                
class Authorization: 
    @staticmethod
    def comparison_to_base(login, password):
        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, password, flag_role FROM User WHERE login = ?", (login,))
            user = cursor.fetchone()
            if not user:
                return (False, "Пользователь с таким login не найден")
            user_id, hashed_password, flag_role = user

            if Checkers.check_hashed_password(password, hashed_password):
                return (True, user_id, flag_role)
            else:
                return (False, "Неверный пароль")
            
        except sqlite3.Error as e:
            return (False)
        finally:
            conn.close()


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        second_name = request.form.get("second_name")
        patronymic = request.form.get("patronymic")
        login = request.form.get("login")
        email = request.form.get("email")
        age = request.form.get("age")
        password = request.form.get("password")
        flag_role = 0
        
        errors = Checkers.check_registration(first_name, second_name, patronymic, login, email, age, password)
        
        if not errors:
            result = Registration.add_to_base(first_name, second_name, patronymic, login, email, age, password, flag_role)
            if result[0]:
                _, user_id, flag_role = result
                session["user"] = {"id": user_id, "email": email, "role": flag_role}
                return redirect(url_for('main_page'))
            else:
                errors.append(result[1])
        return render_template("registration.html", errors=errors)
    return render_template("registration.html", errors=[])



@app.route("/authorization", methods=["GET", "POST"])
def authorization():
    if request.method == "POST":
        
        
        login = request.form.get("login")
        password = request.form.get("password")
        
        errors = Checkers.check_authorization(login, password)
        
        if not errors:
            auth_result = Authorization.comparison_to_base(login, password)
            if auth_result[0]:
                user_id, flag_role = auth_result[1], auth_result[2]
                session["user"] = {"id": user_id, "login": login, "role": flag_role}
                
                admin_flag = Checkers.admin_checker(user_id)
                
                if admin_flag == 1:
                     return redirect(url_for('admin_page'))  
                   
                return redirect(url_for('main_page'))
            else:
                errors.append(auth_result[1])
                
        return render_template("authorization.html", errors=errors)
    return render_template("authorization.html", errors=[])


@app.route("/")
def index():
    return redirect(url_for('authorization'))

@app.route("/login")
def login():
    if "user" in session:
        return render_template("login.html")
    return redirect(url_for('authorization'))

@app.route("/main_page")
def main_page():
    if "user" not in session:
        return redirect(url_for('authorization'))
    return render_template("main_page.html", user=session["user"])

@app.route("/admin_page")
def admin_page():
    if "user" not in session:
        return redirect(url_for('authorization'))
    
    user = session["user"]
    
    if user["role"] != 1:
        return redirect(url_for('main_page'))
    return render_template("admin_page.html", user=user)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('authorization'))

if __name__ == "__main__":
    app.run(debug=True)