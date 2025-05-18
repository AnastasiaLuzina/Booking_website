from flask import Flask, session, request, render_template, redirect, url_for
import sqlite3
import bcrypt
import re
from bcrypt import checkpw  # Импортируем checkpw отдельно

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

class Checkers:
    @staticmethod
    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    @staticmethod
    def is_email_unique(email):
        conn = sqlite3.connect("booking_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        return user is None

    @staticmethod
    def check_registration(first_name, second_name, patronymic, email, age, password):
        errors = []
        
        # Проверка заполнения всех полей
        if not all([first_name, second_name, patronymic, email, age, password]):
            errors.append("Заполните все поля")
        else:
            # Проверка ФИО
            if not all(isinstance(name, str) for name in [first_name, second_name, patronymic]):
                errors.append("ФИО не должны содержать цифры или символы")
            
            # Проверка возраста
            try:
                age = int(age)
                if not 18 <= age <= 100:
                    errors.append("Возраст должен быть от 18 до 100 лет")
            except ValueError:
                errors.append("Возраст должен быть числом")
            
            # Проверка email
            if not Checkers.is_valid_email(email):
                errors.append("Некорректный email")
            elif not Checkers.is_email_unique(email):
                errors.append("Этот email уже занят")
        
        return errors

    @staticmethod
    def check_authorization(email, password):
        errors = []
        
        # Проверка заполнения полей
        if not email or not password:
            errors.append("Заполните все поля")
        else:
            # Проверка email формата
            if not Checkers.is_valid_email(email):
                errors.append("Некорректный email")
            
            # Проверка существования пользователя
            conn = sqlite3.connect("booking_database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM User WHERE email = ?", (email,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                errors.append("Пользователь не найден")
            else:
                # Проверка пароля
                if not checkpw(password.encode(), user[5]):
                    errors.append("Неверный пароль")
        
        return errors
    
class Registration:    
         
    @staticmethod
    def add_to_base(first_name, second_name, patronymic, email, age, password, flag_role):
        conn = sqlite3.connect("booking_database.db")
        cursor = conn.cursor()
        
        try:
            hashed_password = Checkers.hash_password(password)
            cursor.execute('''
                INSERT INTO User (
                    first_name, second_name, patronymic, email, age, password, flag_role
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (first_name, second_name, patronymic, email, age, hashed_password, flag_role))
            
            conn.commit()
            print("Данные успешно добавлены!")
            return True, "Успех"
        
        except sqlite3.IntegrityError as e:
            return False, f"Ошибка: {e}. Возможно, email уже существует."
        
        except Exception as e:
            return False, f"Произошла ошибка: {e}"
        
        finally:
            conn.close()
                
    # ИСПРАВЛЕНИЕ: Метод login_user должен обрабатывать POST-запрос
    @app.route("/registration", methods=["GET", "POST"])
    def login_user():
        if request.method == "POST":
            first_name = request.form.get("first_name")
            second_name = request.form.get("second_name")
            patronymic = request.form.get("patronymic")
            email = request.form.get("email")
            age = request.form.get("age")
            password = request.form.get("password")
            flag_role = request.form.get("flag_role", 0)
            
            # ИСПРАВЛЕНИЕ: Вызов через класс Checkers
            errors = Checkers.check_registration(first_name, second_name, patronymic, email, age, password)
            
            if not errors:
                # ИСПРАВЛЕНИЕ: Используем hash_password вместо hesh_password
                success, message = Registration.add_to_base(
                    first_name, second_name, patronymic, email, age, password, flag_role
                )
                if success:
                    session["user"] = email
                    return redirect(url_for('main_page'))
                else:
                    errors.append(message)
            
            return render_template("registration.html", errors=errors)
        
        return render_template("registration.html", errors=[])
            
class Authorization: 
    @staticmethod
    def comparison_to_base(email, password):
        try:
            conn = sqlite3.connect("booking_database.db")  # ИСПРАВЛЕНИЕ: Используем ту же БД
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id, password, flag_role FROM User WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                return (False, "Пользователь с таким email не найден")
            
            user_id, hashed_password, flag_role = user
            
            if checkpw(password.encode('utf-8'), hashed_password):
                return (True, user_id, flag_role)
            else:
                return (False, "Неверный пароль")
        
        except sqlite3.Error as e:
            return (False, f"Ошибка базы данных: {str(e)}")
        
        finally:
            conn.close()    
     
    # ИСПРАВЛЕНИЕ: Метод обрабатывает POST-запросы
    @app.route("/authorization", methods=["GET", "POST"])
    def find_user():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            
            # ИСПРАВЛЕНИЕ: Вызов через класс Checkers
            errors = Checkers.check_authorization(email, password)
            
            if not errors:
                # ИСПРАВЛЕНИЕ: Вызов comparison_to_base через класс Authorization
                auth_result = Authorization.comparison_to_base(email, password)
                
                if auth_result[0]:
                    user_id, flag_role = auth_result[1], auth_result[2]
                    session["user"] = {"id": user_id, "email": email, "role": flag_role}
                    return redirect(url_for('main_page'))
                else:
                    errors.append(auth_result[1])
            
            return render_template("authorization.html", errors=errors)
        
        return render_template("authorization.html", errors=[])

# ИСПРАВЛЕНИЕ: Убираем классы login_route и main_route
# Создаем отдельные маршруты с декораторами
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

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for('authorization'))

if __name__ == "__main__":
    app.run(debug=True)