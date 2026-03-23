from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import utils.crypto
from database.models import db, User, Service, Subscription
from parser.engine import sync_all_subscriptions
import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("db_url")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# регистрация
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    imap_password = data.get('imap_password')

    if not all([email, password, imap_password]):
        return jsonify({"error": "Missing email, password or IMAP token"}), 400
    
    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify({"error": "User already exists"}), 409
    
    # 1. Создаем объект юзера
    new_user = User(email=email)
    
    # 2. Хешируем пароль от аккаунта (в базу полетит каша)
    new_user.set_password(password)
    
    # 3. Шифруем IMAP пароль (в базу полетит зашифрованная строка)
    new_user.imap_password = utils.crypto.encrypt_imap(imap_password)

    db.session.add(new_user)
    db.session.commit()

    # 4. Запускаем парсинг. 
    # ВАЖНО: передаем чистый imap_password, который пришел из запроса!
    service = Service.query.all()
    print(f"scan postbox for {email}...")
    sync_result = sync_all_subscriptions(email, imap_password, service, is_first_run=True)

    if sync_result["status"] == 'success':
        for item in sync_result['data']:
            sub = Subscription(
                service_id=item['service_id'],
                price=item['amount'],
                start_date=item['payment_date'],
                end_date=item['end_date'],
                user_id=new_user.id,
                category=item['category']
            )
            db.session.add(sub)

        db.session.commit()
        return jsonify({
            "status": "success", 
            "found": len(sync_result['data'])
        }), 201

    return jsonify({"status": "partial_success", "message": "User created but IMAP failed"}), 202

# вход в аккаунт
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Неверный логин или пароль"}), 401

    user_subs = []
    for sub in user.subscriptions:
        user_subs.append({
            "id": sub.id,
            "service_name": sub.service.name,
            "price": sub.price,
            "category": sub.category,
            "clicks": sub.clicks,
            "start_date": sub.start_date.strftime('%Y-%m-%d'),
            "end_date": sub.end_date.strftime('%Y-%m-%d') if sub.end_date else "Active"
        })

    return jsonify({
        "status": "success",
        "user_email": user.email,
        "subscriptions": user_subs
    }), 200


# обновление в приложении
@app.route('/api/sync', methods=['POST'])
def sync_data():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Неверный логин или пароль"}), 401

    # РАСШИФРОВЫВАЕМ пароль IMAP для входа в почту
    try:
        real_imap_pass = utils.crypto.decrypt_imap(user.imap_password)
    except Exception as e:
        return jsonify({"status": "error", "message": "Ошибка ключа шифрования"}), 500

    all_services = Service.query.all()

    # Передаем РЕАЛЬНЫЙ пароль в парсер
    sync_result = sync_all_subscriptions(user.email, real_imap_pass, all_services, is_first_run=False)

    if sync_result['status'] == 'success':
        new_count = 0
        for item in sync_result['data']:
            existing = Subscription.query.filter_by(
                user_id=user.id, 
                service_id=item['service_id'],
                start_date=item['payment_date']
            ).first()

            if not existing:
                new_sub = Subscription(
                    user_id=user.id,
                    service_id=item['service_id'],
                    price=item['amount'],
                    start_date=item['payment_date'],
                    end_date=item['end_date'],
                    category=item['category'] # <--- НЕ ЗАБЫВАЕМ
                )
                db.session.add(new_sub)
                new_count += 1
        
        db.session.commit()
        return jsonify({"status": "success", "added": new_count}), 200
    
    return jsonify({"status": "error", "message": "Sync failed"}), 500

# вывод всех подписок по имейлу
@app.route('/api/subscriptions/by-email', methods=['POST'])
def get_subs_by_email():
    data = request.get_json()
    email = data.get('email')
    
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    subs_list = [{
        "id": s.id,
        "service_name": s.service.name,
        "price": s.price,
        "category": s.category,
        "start_date": s.start_date.strftime('%d.%m.%Y'),
        "end_date": s.end_date.strftime('%d.%m.%Y'),
        "clicks": s.clicks
    } for s in user.subscriptions]

    return jsonify({"status": "success", "subscriptions": subs_list}), 200

# прием запроса на удаление подписки
@app.route('/api/subscription/<int:sub_id>', methods=['DELETE'])
def delete_subscription(sub_id):
    sub = Subscription.query.get(sub_id)
    
    if not sub:
        return jsonify({"status": "error", "message": "Subscription not found"}), 404

    try:
        db.session.delete(sub)
        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": f"Subscription {sub_id} deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# прием изменений данных подписки
@app.route('/api/subscription/<int:sub_id>', methods=['PUT'])
def update_subscription_full(sub_id):
    data = request.get_json()
    sub = Subscription.query.get(sub_id)
    
    if not sub:
        return jsonify({"status": "error", "message": "Subscription not found"}), 404

    try:
        sub.price = data.get('price', sub.price)
        
        # Обработка дат (конвертируем из строки в объект date)
        if 'start_date' in data:
            sub.start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in data:
            val = data.get('end_date')
            sub.end_date = datetime.datetime.strptime(val, '%Y-%m-%d').date() if val else None

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Subscription fully updated",
            "data": {
                "id": sub.id,
                "price": sub.price,
                "start_date": str(sub.start_date),
                "end_date": str(sub.end_date) if sub.end_date else None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Update failed: {str(e)}"}), 500
    
# запрос на клик
@app.route('/api/subscription/<int:sub_id>/click', methods=['POST'])
def increment_subscription_click(sub_id):
    # Ищем подписку в базе
    sub = Subscription.query.get(sub_id)
    
    if not sub:
        return jsonify({
            "status": "error", 
            "message": "Subscription not found"
        }), 404

    try:
        # Инкрементируем счетчик
        sub.clicks = (sub.clicks or 0) + 1
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "Click registered",
            "new_clicks": sub.clicks,
            # Сразу считаем "цену одного использования" для фронта
            "cost_per_click": round(sub.price / sub.clicks, 2) if sub.clicks > 0 else sub.price
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500
    

# запрос на редакт категории
@app.route('/api/subscriptions/<int:sub_id>/category', methods=['PATCH'])
def update_category(sub_id):
    data = request.get_json()
    new_category = data.get('category')
    
    if not new_category:
        return jsonify({"status": "error", "message": "Категория не указана"}), 400
    
    # Ищем подписку
    sub = Subscription.query.get(sub_id)
    
    if not sub:
        return jsonify({"status": "error", "message": "Подписка не найдена"}), 404
        
    # Обновляем
    sub.category = new_category
    db.session.commit()
    
    return jsonify({
        "status": "success", 
        "message": "Категория обновлена",
        "new_category": sub.category
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)