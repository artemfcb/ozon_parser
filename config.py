import os 
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

# Настройки парсеров
PARSER_CONFIG = {
    'timeout': 10,
    'max_products': 5,
    'retry_count': 3
}

# Настройки планировщика
SCHEDULER_CONFIG = {
    'check_interval_minutes': 30,  # Интервал проверки цен
    'retry_delay_minutes': 5,      # Задержка при ошибке
    'max_workers': 3               # Максимальное количество потоков
}

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}