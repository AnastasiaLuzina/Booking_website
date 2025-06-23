from flask import Blueprint, session, render_template, redirect, url_for
from controllers.hallController import Halls_actions
from controllers.equipmentController import EquipmentActions
from controllers.userController import Checkers as UserActions  # Изменено здесь
from controllers.bookingController import BookingActions
from controllers.photoController import PhotoService

import base64 

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    user = session.get("user")
    halls = Halls_actions.get_top_three_halls()
    return render_template("main.html", user=user, halls=halls)

@main_bp.route("/catalog_page")
def catalog_page():
    user = session.get("user")
    halls = Halls_actions.get_halls_with_photos()
    return render_template("catalog.html", halls=halls, user=user)

@main_bp.route("/about_page")
def about_page():
    user = session.get("user")
    return render_template("about.html", user=user)

@main_bp.route("/admin_page")
def admin_page():
    if "user" not in session:
        return redirect(url_for('user.authorization'))
    
    user = session["user"]
    
    if user["role"] != 1:
        return redirect(url_for('main.index'))
    
    # Получаем данные для всех вкладок
    halls = Halls_actions.get_all_halls()
    equipment_list = EquipmentActions.get_all_equipment_with_halls()
    users = UserActions.get_all_users()
    bookings = BookingActions.get_all_bookings()
    
    # Получаем первые фото для залов
    hall_photos = {}
    for hall in halls:
        photo = PhotoService.get_first_photo_by_hall(hall[0])
        if photo:
            hall_photos[hall[0]] = base64.b64encode(photo[0]).decode('utf-8')
    
    return render_template("admin_page.html", 
                          user=user, 
                          halls=halls,
                          equipment_list=equipment_list,
                          users=users,
                          bookings=bookings,
                          hall_photos=hall_photos)