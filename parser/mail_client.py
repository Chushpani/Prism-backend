import imaplib
import email
from email.header import decode_header

class MailClient:
    SERVERS = {
        "gmail.com": "imap.gmail.com",
        "yandex.ru": "imap.yandex.ru",
        "mail.ru": "imap.mail.ru",
        "list.ru": "imap.mail.ru",
        "bk.ru": "imap.mail.ru",
        "inbox.ru": "imap.mail.ru"
    }

    def __init__(self, user, password):
        self.user = user
        self.password = password
        domain = user.split("@")[-1]

        self.imap_url = self.SERVERS.get(domain, "imap.gmail.com")
        self.mail = None

    def connect(self):
        try:
            # Подключаемся к серверу Google
            self.mail = imaplib.IMAP4_SSL(self.imap_url)
            # Пытаемся залогиниться
            self.mail.login(self.user, self.password)
            print("✅ Красава! Мы внутри!")
            return True
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def search_by_service(self, service):
        # поиск писем по шаблонным адресам
        self.mail.select('INBOX')
        search_query = f'(FROM "{service.sender_email}")'.encode('utf-8')
        status, data = self.mail.search('UTF-8', search_query)
        
        if status != 'OK':
            return []

        all_ids = data[0].split()
        print(f"🔎 Найдено всего писем от {service.name}: {len(all_ids)}")

        return all_ids
    
    def get_raw_email(self, msg_id):
        # достает грязную внутрянку
        status, data = self.mail.fetch(msg_id, '(RFC822)')
        
        if status != 'OK':
            return None

        raw_bytes = data[0][1]
        
        msg = email.message_from_bytes(raw_bytes)
        
        return msg
    
    def get_email_body(self, msg):
        # вытаскиваем чисты html из письма
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        return ""
    
    def logout(self):
        """Культурно закрываем соединение, чтобы сервер не ругался"""
        if self.mail:
            try:
                self.mail.close() 
                self.mail.logout()
                print("🚪 Сессия IMAP закрыта. До связи!")
            except Exception as e:
                print(f"⚠️ Не удалось закрыть сессию (возможно, уже отвалилась): {e}")


# --- ТЕСТОВЫЙ ЗАПУСК ---
if __name__ == "__main__":
    from scraper import extract_amount, extract_date, extract_duration_and_calculate_end
    
    MY_EMAIL = "platongimp96@gmail.com"
    MY_PASS = "womr khiz tdmw yejl" # Надеюсь, ты его потом сменишь ;)
    
    client = MailClient(MY_EMAIL, MY_PASS)
    client.connect()

    # Временно создаем структуру сервиса для теста
    from collections import namedtuple
    Service = namedtuple('Service', ['name', 'sender_email', 'search_keywords'])
    
    # Тестим на том самом адресе кента/ОФД, который сработал
    target_service = Service("Yandex Plus (Test)", "yarik-top1@yandex.ru", "Плюс")

    ids = client.search_by_service(target_service)
    
    if ids:
        print(f"🔎 Найдено писем: {len(ids)}")
        last_id = ids[-1]
        msg = client.get_raw_email(last_id)
        body = client.get_email_body(msg)

        # 1. Извлекаем дату письма (старт подписки)
        start_date = extract_date(msg)
        
        # 2. Извлекаем сумму
        price = extract_amount(body)
        
        # 3. Считаем дату окончания (Вариант Б)
        if start_date:
            end_date = extract_duration_and_calculate_end(start_date, body)
        
        print(f"\n--- ОТЧЕТ ПАРСЕРА ---")
        print(f"✅ Тема: {msg['Subject']}")
        print(f"💰 Сумма: {price if price else 'НЕ НАЙДЕНА'} руб.")
        print(f"📅 Дата списания: {start_date}")
        print(f"⌛ Конец подписки: {end_date if start_date else 'НЕ ОПРЕДЕЛЕНА'}")
        print(f"----------------------")
    else:
        print(f"❌ Писем от {target_service.sender_email} не найдено.")

