from flask import Blueprint, session, render_template, redirect, url_for, request, flash, jsonify
from datetime import datetime, timedelta, time, date
import sqlite3
from collections import defaultdict
from tools.tools_for_base import connect_to_base, close_base, commit_in_base

from .hallController import Halls_actions

import json

booking_bp = Blueprint('booking', __name__)

# Словарь для хранения состояния слотов в памяти
# Формат: {hall_id: {date: {'available': [], 'booked': []}}}
time_slots_cache = defaultdict(lambda: defaultdict(dict))

class BookingActions:
    
    @staticmethod
    def get_available_slots(hall_id, date):
        conn, cursor = connect_to_base()
        try:
            # Получаем занятые слоты
            cursor.execute("""
                SELECT start_time
                FROM Bookings
                WHERE hall_id = ? AND date = ? AND status = 'confirmed'
            """, (hall_id, date))
            booked_slots = [row[0] for row in cursor.fetchall()]
            
            # Генерируем все возможные слоты
            all_slots = []
            for hour in range(9, 17):
                for minute in [0, 15, 30, 45]:
                    time_str = f"{hour}:{minute:02d}"
                    all_slots.append(time_str)
            
            # Фильтруем доступные слоты
            available_slots = [slot for slot in all_slots if slot not in booked_slots]
            
            return {
                'available_slots': available_slots,
                'booked_slots': booked_slots
            }
        finally:
            close_base(conn)
        
    
    
    @staticmethod
    def generate_time_slots():
        """Генерирует список временных слотов с 10:00 до 21:00 с шагом 30 минут"""
        slots = []
        current_time = time(10, 0)
        end_time = time(21, 0)
        
        while current_time < end_time:
            slot_end = (datetime.combine(date.today(), current_time) + timedelta(minutes=30))
            slot_end_time = slot_end.time()
            
            if slot_end_time > end_time:
                break
                
            slots.append({
                'start': current_time.strftime('%H:%M'),
                'end': slot_end_time.strftime('%H:%M'),
                'label': f"{current_time.strftime('%H:%M')}-{slot_end_time.strftime('%H:%M')}"
            })
            
            current_time = slot_end_time
        
        return slots

    @staticmethod
    def get_bookings_for_date(hall_id, booking_date):
        """Получает бронирования для конкретного зала и даты"""
        conn, cursor = connect_to_base()
        try:
            cursor.execute("""
                SELECT start_time, end_time 
                FROM Bookings 
                WHERE hall_id = ? AND date = ? AND status = 'confirmed'
            """, (hall_id, booking_date))
            return cursor.fetchall()
        except sqlite3.Error:
            return []
        finally:
            close_base(conn)

    @staticmethod
    def update_slots_cache(hall_id, booking_date):
        """Обновляет кэш слотов для конкретного зала и даты"""
        # Получаем базовые слоты
        all_slots = BookingActions.generate_time_slots()
        slot_labels = [slot['label'] for slot in all_slots]
        
        # Получаем бронирования
        bookings = BookingActions.get_bookings_for_date(hall_id, booking_date)
        
        # Помечаем занятые слоты
        booked_slots = set()
        for booking in bookings:
            start_time = booking[0]
            end_time = booking[1]
            
            # Находим все слоты, которые пересекаются с бронированием
            for slot in all_slots:
                if start_time <= slot['end'] and end_time >= slot['start']:
                    booked_slots.add(slot['label'])
        
        # Обновляем кэш
        time_slots_cache[hall_id][booking_date] = {
            'available': [label for label in slot_labels if label not in booked_slots],
            'booked': list(booked_slots)
        }
    
    @staticmethod
    def get_available_dates():
        """Возвращает список доступных дат (текущая + 13 дней)"""
        today = datetime.today().date()
        return [today + timedelta(days=i) for i in range(14)]
    
    @staticmethod
    def check_booking_availability(hall_id, booking_date, start_time, end_time):
        """Проверяет доступность временного интервала"""
        # Обновляем кэш перед проверкой
        BookingActions.update_slots_cache(hall_id, booking_date)
        
        # Получаем слоты для интервала
        all_slots = BookingActions.generate_time_slots()
        interval_slots = []
        
        current = datetime.strptime(start_time, '%H:%M').time()
        end = datetime.strptime(end_time, '%H:%M').time()
        
        while current < end:
            slot_end = (datetime.combine(date.today(), current) + timedelta(minutes=30)).time()
            if slot_end > end:
                break
                
            # Находим метку слота
            for slot in all_slots:
                if slot['start'] == current.strftime('%H:%M'):
                    interval_slots.append(slot['label'])
                    break
            
            current = slot_end
        
        # Проверяем, все ли слоты доступны
        available_slots = time_slots_cache[hall_id][booking_date]['available']
        return all(slot in available_slots for slot in interval_slots)
    
    @staticmethod
    def create_booking(user_id, hall_id, booking_date, start_time, end_time):
        """Создает бронирование в базе данных"""
        conn, cursor = connect_to_base()
        try:
            # Рассчитываем продолжительность
            start_dt = datetime.strptime(start_time, '%H:%M')
            end_dt = datetime.strptime(end_time, '%H:%M')
            duration = (end_dt - start_dt).total_seconds() / 60  # в минутах
            
            # Создаем бронирование
            cursor.execute("""
                INSERT INTO Bookings (user_id, hall_id, date, start_time, end_time, duration, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, hall_id, booking_date, start_time, end_time, duration, 'confirmed'))
            
            commit_in_base(conn)
            
            # Обновляем кэш
            BookingActions.update_slots_cache(hall_id, booking_date)
            
            return True, "Бронирование успешно создано"
        except sqlite3.Error as e:
            return False, f"Ошибка при создании брони: {str(e)}"
        finally:
            close_base(conn)

@booking_bp.route("/booking/<int:hall_id>", methods=['GET'])
def booking_main(hall_id):
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    hall = Halls_actions.get_hall_by_id(hall_id)
    
    # Генерация данных для календаря
    today = datetime.today()
    week_days = []
    for i in range(7):
        day = today + timedelta(days=i)
        week_days.append({
            'name': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][day.weekday()],
            'date': day.day
        })
    
    # Генерация временных слотов
    time_slots = []
    for hour in range(9, 17):
        for minute in ['00', '15', '30', '45']:
            time_slots.append(f"{hour}:{minute}")
    
    return render_template(
        "booking.html",
        hall=hall,
        week_days=week_days,
        time_slots=time_slots,
        current_date=datetime.now().strftime("%B %Y")
    )
    

@booking_bp.route("/booking/slots", methods=['GET'])
def get_slots():
    hall_id = request.args.get('hall_id')
    booking_date = request.args.get('date')
    
    if not hall_id or not booking_date:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        # Генерируем все возможные слоты (9:00-16:45 с шагом 15 мин)
        all_slots = []
        for hour in range(9, 17):
            for minute in [0, 15, 30, 45]:
                if hour == 16 and minute > 45:
                    continue
                all_slots.append(f"{hour}:{minute:02d}")
        
        # Здесь должна быть логика получения занятых слотов из БД
        # Заглушка для примера:
        booked_slots = []
        if hour % 2 == 0:  # Пример: каждый четный час занят
            booked_slots = [f"{hour}:{minute:02d}" for hour in range(10, 17, 2) for minute in [0, 15, 30, 45]]
        
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return jsonify({
            'available': available_slots,
            'booked': booked_slots
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@booking_bp.route("/booking/select_time", methods=['GET', 'POST'])
def select_time():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    if request.method == 'POST':
        session['booking_data'] = {
            'hall_id': request.form['hall_id'],
            'date': request.form['date']
        }
        return redirect(url_for('booking.select_time'))
    
    booking_data = session.get('booking_data', {})
    hall_id = booking_data.get('hall_id')
    date = booking_data.get('date')
    
    if not hall_id or not date:
        return redirect(url_for('booking.booking_main'))
    
    # Обновляем кэш слотов
    BookingActions.update_slots_cache(hall_id, date)
    
    return render_template(
        "select_time.html",
        hall_id=hall_id,
        date=date,
        selected_start_time=session.get('selected_start_time')
    )

@booking_bp.route("/booking/select_start/<start_time>")
def select_start(start_time):
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    session['selected_start_time'] = start_time
    return redirect(url_for('booking.select_time'))


@booking_bp.route("/booking/select_end", methods=['POST'])
def select_end():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    booking_data = session.get('booking_data', {})
    start_time = session.get('selected_start_time')
    end_time = request.form['end_time']
    
    if not booking_data or not start_time or not end_time:
        return redirect(url_for('booking.booking_main'))
    
    hall_id = booking_data['hall_id']
    date = booking_data['date']
    
    # Проверяем доступность
    is_available = BookingActions.check_booking_availability(
        hall_id, date, start_time, end_time
    )
    
    if not is_available:
        flash("Выбранные слоты времени уже заняты", "danger")
        return redirect(url_for('booking.select_time'))
    
    # Рассчитываем продолжительность
    start_dt = datetime.strptime(start_time, '%H:%M')
    end_dt = datetime.strptime(end_time, '%H:%M')
    duration = (end_dt - start_dt).total_seconds() / 60
    
    # Сохраняем данные для подтверждения
    session['booking_confirmation'] = {
        **booking_data,
        'start_time': start_time,
        'end_time': end_time,
        'duration': duration
    }
    
    return redirect(url_for('booking.confirm_booking'))

@booking_bp.route("/booking/confirm", methods=['GET', 'POST'])
def confirm_booking():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    booking_data = session.get('booking_confirmation', {})
    
    if not booking_data:
        return redirect(url_for('booking.booking_main'))
    
    if request.method == 'POST':
        user_id = session['user']['id']
        success, message = BookingActions.create_booking(
            user_id,
            booking_data['hall_id'],
            booking_data['date'],
            booking_data['start_time'],
            booking_data['end_time']
        )
        
        if success:

            session.pop('booking_data', None)
            session.pop('selected_start_time', None)
            session.pop('booking_confirmation', None)
            
            flash("Бронирование успешно создано!", "success")
            return redirect(url_for('main.main_page'))
        else:
            flash(message, "danger")
    
    hall = Halls_actions.get_hall_by_id(booking_data['hall_id'])
    
    # Форматируем время для отображения
    start_time = datetime.strptime(booking_data['start_time'], '%H:%M').strftime('%H:%M')
    end_time = datetime.strptime(booking_data['end_time'], '%H:%M').strftime('%H:%M')
    duration_hours = int(booking_data['duration'] // 60)
    duration_minutes = int(booking_data['duration'] % 60)
    duration_str = f"{duration_hours} ч. {duration_minutes} мин." if duration_hours else f"{duration_minutes} мин."
    
    return render_template(
        "confirm_booking.html",
        booking={
            **booking_data,
            'start_time': start_time,
            'end_time': end_time,
            'duration_str': duration_str
        },
        hall=hall
    )