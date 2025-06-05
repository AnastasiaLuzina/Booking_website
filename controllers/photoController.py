from flask import Blueprint, session, request, render_template, redirect, url_for
from tools.tools_for_base import connect_to_base, close_base
import base64

photo_bp = Blueprint('photo', __name__)

class Photo_actions:
    @staticmethod
    def get_photos_by_hall(hall_id, errors):
        
        try:
            conn, cursor = connect_to_base()
            cursor.execute("""
                SELECT photo_id, photo_bytes 
                FROM Photo 
                WHERE hall_id = ?
                ORDER BY photo_id
            """, (hall_id,))
            close_base(conn)
            return cursor.fetchall()
        except Exception as e:
            errors.append(f"Ошибка базы данных: {e}")
            return None
        
        

@photo_bp.route("/hall_photos/<int:hall_id>", methods=["GET"])
def get_photos_page(hall_id):
    errors = []
    photos = Photo_actions.get_photos_by_hall(hall_id, errors)
    
    if errors:
        return render_template("error.html", errors=errors)
        
    return render_template(
        "hall_photos.html",
        photos=[base64.b64encode(p[1]).decode('utf-8') for p in photos]
    )