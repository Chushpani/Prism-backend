from flask import request, jsonify, Blueprint
from parser.engine import sync_all_subscriptions
from database.models import db, Service, Subscription

api_bp = Blueprint('api', __name__)

@api_bp.route('/sync', methods=['POST'])
def sync():
    # 1. Получаем данные от кента (из C# приложения)
    data = request.json
    user_email = data.get('email')
    user_password = data.get('password')
    is_first_auth = data.get('first_run', False) # Кент сам скажет, первая это рега или нет

    services = Service.query.all()

    # 2. Твой парсер делает магию
    # (Допустим, services мы берем из базы)
    sync_result = sync_all_subscriptions(user_email, user_password, services, is_first_run=is_first_auth)

    # 3. Плюемся JSON-ом обратно в C#
    return jsonify(sync_result)