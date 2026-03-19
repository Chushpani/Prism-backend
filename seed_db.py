from app import app
from database.models import db, Service

def seed_services():
    # Создаем список топ сервисов
    services_to_add = [
    Service(
        name="Yandex Plus", 
        sender_email="no-reply@plus.yandex.ru", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=yandex.ru",
        search_keywords="Плюс,Списание,Заказ"
    ),
    Service(
        name="Spotify", 
        sender_email="no-reply@spotify.com", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=spotify.com",
        search_keywords="Receipt,Subscription,Счёт"
    ),
    Service(
        name="Netflix", 
        sender_email="info@mailer.netflix.com", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=netflix.com",
        search_keywords="Your plan,Update,Payment"
    ),
    Service(
        name="Ivi", 
        sender_email="support@ivi.ru", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=ivi.ru",
        search_keywords="Подписка,Оплата,ivi"
    ),
    Service(
        name="Telegram Premium", 
        sender_email="premium@telegram.org", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=telegram.org",
        search_keywords="Premium,Receipt,Fragment"
    ),
    Service(
        name="VK Music", 
        sender_email="support@vk.com", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=vk.com",
        search_keywords="VK Music,Подписка,Выписка"
    ),
    Service(
        name="Okko", 
        sender_email="mail@okko.tv", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=okko.tv",
        search_keywords="Оплата,Okko,Чек,Подписка"
    ),
    Service(
        name="Premier", 
        sender_email="help@premier.one", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=premier.one",
        search_keywords="Premier,Оплата,Подписка"
    ),
    Service(
        name="Start", 
        sender_email="support@start.ru", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=start.ru",
        search_keywords="Start,Оплата,Подписка"
    ),
    Service(
        name="Apple Services", 
        sender_email="no_reply@email.apple.com", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=apple.com",
        search_keywords="Invoice,Квитанция,Apple"
    ),
    Service(
        name="ChatGPT", 
        sender_email="info@sendgrid.openai.com", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=openai.com",
        search_keywords="Invoice,Subscription,Renewal"
    ),
    Service(
        name="YouTube Premium", 
        sender_email="noreply@youtube.com", 
        logo_url="https://www.google.com/s2/favicons?sz=64&domain=youtube.com",
        search_keywords="Membership,Receipt,Подписка"
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