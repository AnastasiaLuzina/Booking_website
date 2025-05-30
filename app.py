from controllers.userController import user_bp
from controllers.hallController import hall_bp  # Импорт Blueprint для залов
from flask import Flask

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Секретный ключ

# Регистрация обоих Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(hall_bp) 

if __name__ == "__main__":
    app.run(debug=True)