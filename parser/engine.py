from .mail_client import MailClient
from .scraper import extract_amount, extract_date, extract_duration_and_calculate_end
import datetime

def sync_engine(client, service, full_scan=False):
    ids = client.search_by_service(service)
    if not ids:
        return []

    target_ids = ids if full_scan else ids[-5:]
    
    found_payments = []
    
    for msg_id in reversed(target_ids):
        msg = client.get_raw_email(msg_id)
        body = client.get_email_body(msg)
        
        price = extract_amount(body)
        if price:
            p_date = extract_date(msg)
            p_end = extract_duration_and_calculate_end(p_date, body)
            
            found_payments.append({
                "service_id": service.id,
                "amount": price,
                "payment_date": p_date,
                "end_date": p_end
            })
            
            
            if not full_scan:
                break
                
    return found_payments

def sync_all_subscriptions(email, password, services_from_db, is_first_run=False):
    client = MailClient(email, password)
    
    if not client.connect():
        return {"status": "error", "message": "Failed to connect to mail"}

    all_found_data = []

    try:
        for service in services_from_db:
            print(f"🔎 Обработка: {service.name} (Режим: {'Полный' if is_first_run else 'Быстрый'})")
            
            # Вызываем нашу универсальную функцию
            payments = sync_engine(client, service, full_scan=is_first_run)
            
            if payments:
                all_found_data.extend(payments)
                print(f"✅ Найдено транзакций: {len(payments)}")
            else:
                print(f"❌ Чеков не найдено.")
    
    except Exception as e:
        print(f"💥 Критическая ошибка во время парсинга: {e}")
        # Можно даже вернуть частичные данные, если они успели собраться
        return {"status": "error", "message": str(e), "partial_data": all_found_data}
    
    finally:
        # Блок finally выполнится ВСЕГДА: и при успехе, и при ошибке.
        # Это "железный" способ закрыть дверь.
        client.logout()

    return {"status": "success", "data": all_found_data}