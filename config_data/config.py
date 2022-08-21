import os
from dotenv import load_dotenv, find_dotenv
from loguru import logger


if not find_dotenv():
    logger.warning('Переменные окружения не загружены т.к отсутствует файл .env')
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку по командам")
)

CUSTOM_COMMANDS = (
    ('lowprice', "Выводит самые дешевые отели в указанном городе"),
    ('highprice', "Выводит самые дорогие отели в указанном городе"),
    ('bestdeal', "Выводит отели, в указанном диапазоне цены и расстоянии от центра")
)

ADDITIONAL_COMMANDS = (
    ('history', "Выводит историю поиска по отелям"),
    ('favorite', "Выводит избранные отели")
)