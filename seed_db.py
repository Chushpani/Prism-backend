from app import app
from database.models import db, Service

def seed_services():
    # Создаем список "эталонных" сервисов
    services_to_add = [
        Service(
            name="Yandex Plus", 
            sender_email="no-reply@plus.yandex.ru", 
            logo_url="https://example.com/yandex.png"
        ),
        Service(
            name="Spotify", 
            sender_email="no-reply@spotify.com", 
            logo_url="https://example.com/spotify.png"
        ),
        Service(
            name="Netflix", 
            sender_email="info@mailer.netflix.com", 
            logo_url="https://example.com/netflix.png"
        )
    ]

    with app.app_context():
        # Проверяем, нет ли уже этих сервисов, чтобы не дублировать
        for s in services_to_add:
            exists = Service.query.filter_by(name=s.name).first()
            if not exists:
                db.session.add(s)

        db.session.commit()
        print("Шаблоны сервисов успешно добавлены!")

if __name__ == "__main__":
    seed_services()