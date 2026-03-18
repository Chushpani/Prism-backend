from database.models import db, User, Service, Subscription
from datetime import datetime

class DBManager:
    # данные о сервисе подписку по имейлу
    @staticmethod
    def get_service_by_email(email_from):
        service = Service.query.filter_by(sender_email=email_from).first()
        return service
    
    # сохранение найденной подписки
    @staticmethod
    def save_subscription(user_id, service_id, price, start_date, end_date=None):
        sub = Subscription.query.filter_by(
            user_id = user_id,
            service_id = service_id
            ).first()
        
        if sub:
            sub.price = price
            sub.start_date = start_date
            print(f"Обновили подписку ID {service_id} for {user_id}")
            if end_date:
                sub.end_date = end_date
            print(f"Обновили подписку. Конец: {sub.end_date}")
        else:
            sub = Subscription (
                user_id = user_id,
                service_id=service_id,
                price=price,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(sub)

        db.session.commit()

    # вывод данных всех подписок юзера
    @staticmethod
    def get_user_subscriptions(user_id):
        return Subscription.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()