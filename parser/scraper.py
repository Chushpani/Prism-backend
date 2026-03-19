import re
from email.utils import parsedate_to_datetime
from datetime import date, timedelta

def extract_amount(html_body):
    clean_text = re.sub(r'<[^>]+>', ' ', html_body)
    clean_text = clean_text.replace('\xa0', ' ') 
    clean_text = re.sub(r'\s+', ' ', clean_text)

    patterns = [
        r'(?:ИТОГО|ИТОГ|Сумма|К оплате)[\s\w\.]*?(\d[\d\s]*[.,]\d{2})', 
        r'(\d[\d\s]*[.,]?\d{0,2})\s*(?:руб|р\.?|₽|RUB)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            raw_val = match.group(1).replace(' ', '').replace(',', '.')
            try:
                return float(raw_val)
            except ValueError:
                continue
            
    return None

def extract_date(msg):
    raw_date = msg.get('Date')
    if not raw_date:
        return date.today()
    
    try:
        dt = parsedate_to_datetime(raw_date)
        return dt.date()
    except Exception:
        return date.today()
    
def extract_duration_and_calculate_end(start_date, html_body):
    clean_text = re.sub(r'<[^>]+>', ' ', html_body).lower()
    
    year_markers = ['год', 'year', '12 месяц', 'ежегод', 'annual']
    for marker in year_markers:
        if marker in clean_text:
            return start_date + timedelta(days=365)
    
    days_match = re.search(r'на (\d+)\s*(?:день|дня|дней)', clean_text)
    if days_match:
        days = int(days_match.group(1))
        return start_date + timedelta(days=days)

    return start_date + timedelta(days=30)