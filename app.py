from controllers.userController import user_bp  # Импорт Blueprint
from flask import Flask

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Секретный ключ
app.register_blueprint(user_bp)  # Регистрация Blueprint

if __name__ == "__main__":
    app.run(debug=True)