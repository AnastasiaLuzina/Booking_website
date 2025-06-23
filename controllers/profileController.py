from flask import Blueprint, session, request, render_template, redirect, url_for, flash
from tools.tools_for_base import connect_to_base, close_base
import sqlite3
from controllers.userController import Checkers
from controllers.hallController import Halls_actions 
from flask import flash  
profile_bp = Blueprint('profile', __name__)

class Profile_actions:
    
    @staticmethod
    def get_user_bookings(user_id):
        conn, cursor = connect_to_base()
        try:
            cursor.execute("""
                SELECT b.booking_id, h.title, b.date, b.start_time, b.end_time, 
                    CASE WHEN b.status_for_admin = 1 THEN 1 ELSE 0 END as is_active
                FROM Booking b
                JOIN Hall h ON b.hall_id = h.hall_id
                WHERE b.user_id = ?
                ORDER BY b.date DESC, b.start_time DESC
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting user bookings: {str(e)}")
            return []
        finally:
            close_base(conn)
    
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


@profile_bp.route('/profile')
def profile():
    
    
    # Получаем ошибки из сессии (если есть) и очищаем
    errors = session.pop('profile_errors', [])
    
    user_id = session["user"]["id"]
    user_data = Profile_actions.take_info(user_id)
    halls_liked = Halls_actions.get_liked_halls(user_id)
    user_id = session["user"]["id"]
    
    bookings = Profile_actions.get_user_bookings(user_id)
    active_bookings = [b for b in bookings if b[5] == 1]  # Активные (status_for_admin=1)
    past_bookings = [b for b in bookings if b[5] == 0]    # Неактивные

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
        
    return render_template('profile.html', 
                          user=user_info, 
                          errors=errors, 
                          halls=halls_liked,
                          active_bookings=active_bookings,
                          past_bookings=past_bookings)

@profile_bp.route('/profile_edit_page')
def profile_edit_page():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    errors = session.pop('profile_errors', [])
    user_id = session["user"]["id"]
    user_data = Profile_actions.take_info(user_id)
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
        
    return render_template('profile_edit.html', user=user_info, errors=errors)

# Добавим роут для удаления бронирования
@profile_bp.route("/delete_booking/<int:booking_id>", methods=['POST'])
def delete_booking(booking_id):
    if 'user' not in session:
        return redirect(url_for('user.authorization'))
    
    user_id = session['user']['id']
    conn, cursor = connect_to_base()
    try:
        # Проверяем принадлежность бронирования пользователю
        cursor.execute("SELECT 1 FROM Booking WHERE booking_id = ? AND user_id = ?", 
                      (booking_id, user_id))
        if not cursor.fetchone():
            flash("Это бронирование вам не принадлежит", "danger")
            return redirect(url_for('profile.profile'))
        
        # Устанавливаем статус бронирования как отмененное (0)
        cursor.execute("UPDATE Booking SET status_for_admin = 0 WHERE booking_id = ?", (booking_id,))
        conn.commit()
        flash("Бронирование успешно отменено", "success")
    except Exception as e:
        flash(f"Ошибка при отмене бронирования: {str(e)}", "danger")
    finally:
        close_base(conn)
    
    return redirect(url_for('profile.profile'))