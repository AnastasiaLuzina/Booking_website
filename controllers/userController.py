from flask import Flask, session, request, render_template, redirect, url_for
# import sys
# sys.path.append("..\\Booking_website")

from tools.tools_for_base import connect_to_base, close_base, commit_in_base


import sqlite3
import re

import hashlib
import secrets

app = Flask(__name__, template_folder="../templates")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'



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
        cursor = connect_to_base()
        cursor.execute("SELECT * FROM User WHERE login = ?", (login,))
        user = cursor.fetchone()
        close_base()
        return user is None
        
        

    @staticmethod
    def get_hash_password(p: str) -> str:
         # Создаем MD5 хеш
        md5_hash = hashlib.md5()
        
        # Кодируем строку в байты (UTF-8) и обновляем хеш
        md5_hash.update(p.encode('utf-8'))
        
        # Получаем hex-представление хеша
        return md5_hash.hexdigest()
    
    # @staticmethod
    # def check_hashed_password(password, stored_hash):
    #     if not stored_hash or '$' not in stored_hash:
    #         return False
    #     try:
    #         salt, hashed = stored_hash.split('$')
    #         new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    #         return new_hash == hashed
    #     except:
    #         return False

    @staticmethod
    def check_authorization(login, password):
        errors = []
        if not login or not password:
            errors.append("Заполните все поля")
            return errors
            
        # conn = sqlite3.connect(DATABASE)
        # cursor = conn.cursor()
        # try:
        #     cursor.execute("SELECT * FROM User WHERE login = ?", (login,))
        #     user = cursor.fetchone()
            
        #     if not user:
        #         errors.append("Пользователь с таким логином не найден")
        #     else:
        #         if Checkers.get_hash_password(password) != user[5]:
        #             errors.append("Неверный пароль")
        # except sqlite3.Error as e:
        #     errors.append("Ошибка базы данных")
        # finally:
        #     conn.close()
        
        return errors

    @staticmethod
    def is_email_unique(email):
        cursor = connect_to_base()
        cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
        user = cursor.fetchone()
        close_base()
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

    # @staticmethod
    # def check_authorization(login, password):
    #     errors = []
    #     if not login or not password:
    #         errors.append("Заполните все поля")
    #     else:
            
    #         if Checkers.is_login_unique(login):
    #             errors.append("Пользователь с таким логином не найден")
                
    #         conn = sqlite3.connect(DATABASE)
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT * FROM User WHERE login = ?", (login,))
    #         user = cursor.fetchone()
    #         conn.close()
    #         if not user:
    #             errors.append("Пользователь не найден")
    #         else:
    #             if not Checkers.check_hashed_password(password, user[5]):
    #                 errors.append("Неверный пароль")
    #     return errors

    @staticmethod
    def admin_checker(user_id):
        cursor = connect_to_base()
        cursor.execute("SELECT flag_role FROM User WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        return user[0]
            


    
    
class Registration:    
    @staticmethod
    def add_to_base(first_name, second_name, patronymic, login, email, age, password, flag_role):
        cursor = connect_to_base()
        try:
            hashed_password = Checkers.hash_password(password)
            cursor.execute('''
                INSERT INTO User (first_name, second_name, patronymic, login, email, age, password, flag_role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, second_name, patronymic, login, email, age, hashed_password, flag_role))
            user_id = cursor.lastrowid
            commit_in_base()
            return True, user_id, flag_role
        except sqlite3.IntegrityError as e:
            return False, f"Ошибка: {e}"
        except Exception as e:
            return False, f"Произошла ошибка: {e}"
        finally:
            close_base()
                
                
                
class Authorization: 
    @staticmethod
    def comparison_to_base(login, password):
        try:
            cursor = connect_to_base()
            cursor.execute("SELECT user_id, password, flag_role FROM User WHERE login = ? AND password = ?", (login, Checkers.get_hash_password(password)))
            user = cursor.fetchone()
            
            if not user:
                return (False, "Пользователь не найден")
            
            # Возвращаем кортеж (success, data)
            return (True, {
                'user_id': user[0],
                'flag_role': user[2]
            })
            
            # user_id, hashed_password, flag_role = user

            # if Checkers.get_hash_password(password):
            #     
            # else:
            #     return (False, "Неверный пароль")
            
        except sqlite3.Error as e:
            return (False, None)
        finally:
            close_base()


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
        
        errors = Checkers.check_authorization(login, password) #проверка на пустоту полей
        
        if not errors:
            success, auth_data = Authorization.comparison_to_base(login, password)
            
            if success:
                session["user"] = {
                    "id": auth_data['user_id'],
                    "login": login,
                    "role": auth_data['flag_role']
                }
                
                if auth_data['flag_role'] == 1:  # Проверка на админа
                    return redirect(url_for('admin_page'))
                
                return redirect(url_for('main_page'))
            else:
                errors.append(auth_data)  # Добавляем сообщение об ошибке
                
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