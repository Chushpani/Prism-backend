from flask import Flask
from config import Config
from database.models import db

app = Flask(__name__)
app.config.from_object(Config)

# Инициализируем базу данных
db.init_app(app)

# Создаем таблицы при запуске (если их нет)
with app.app_context():
    db.create_all()
    print("База данных Prismdb успешно инициализирована!")

@app.route('/')
def hello():
    return {"message": "Prism API is running"}

if __name__ == '__main__':
    app.run(debug=True)