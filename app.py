from flask import Flask
from controllers.userController import user_bp
from controllers.hallController import hall_bp
from controllers.mainController import main_bp  

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Регистрация всех Blueprint
app.register_blueprint(user_bp)
app.register_blueprint(hall_bp)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)