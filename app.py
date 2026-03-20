from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from database.models import db, User, Service, Subscription
from parser.engine import sync_all_subscriptions
import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("db_url")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    imap_password = data.get('imap_password')

    if not all([email, password, imap_password]):
        return jsonify({"error": "Missing email, password or IMAP token"}), 400
    
    user_exists = User.query.filter_by(email = email).first()
    if user_exists:
        return jsonify({"error": "User already exists"}), 409
    
    new_user = User(
        email = email,
        password = password,
        imap_password = imap_password
    )

    db.session.add(new_user)
    db.session.commit()

    service = Service.query.all()

    print(f"scan postbox for {email}...")
    sync_result = sync_all_subscriptions(email, imap_password, service, is_first_run=True)

    if sync_result["status"] == 'success':
        for item in sync_result['data']:
            sub = Subscription(
                service_id = item['service_id'],
                price=item['amount'],
                start_date=item['payment_date'],
                end_date=item['end_date'],
                user_id=new_user.id
            )
            db.session.add(sub)

        db.session.commit()
        return jsonify({
            "status": "success",
            "found": len(sync_result['data'])
        }), 201

    return jsonify({"status": "partial_success", "message": "User created but IMAP failed"}), 202

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({"status": "error", "message": "Неверный логин или пароль"}), 401

    user_subs = []
    for sub in user.subscriptions:
        user_subs.append({
            "id": sub.id,
            "service_name": sub.service.name,
            "price": sub.price,
            "start_date": sub.start_date.strftime('%Y-%m-%d'),
            "end_date": sub.end_date.strftime('%Y-%m-%d') if sub.end_date else "Active"
        })

    return jsonify({
        "status": "success",
        "user_email": user.email,
        "subscriptions": user_subs
    }), 200

@app.route('/api/sync', methods=['POST'])
def sync_data():
    data = request.get_json()
    user_id = data.get('user_id') 

    user = User.query.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    all_services = Service.query.all()

    sync_result = sync_all_subscriptions(user.email, user.imap_password, all_services, is_first_run=False)

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
                    end_date=item['end_date']
                )
                db.session.add(new_sub)
                new_count += 1
        
        db.session.commit()
        return jsonify({"status": "success", "added": new_count}), 200
    
    return jsonify({"status": "error", "message": "Sync failed"}), 500

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
        "start_date": s.start_date.strftime('%Y-%m-%d')
    } for s in user.subscriptions]

    return jsonify({"status": "success", "subscriptions": subs_list}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)