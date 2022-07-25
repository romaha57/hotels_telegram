import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота и пройти небольшую регистрацию"),
    ('help', "Вывести справку по командам"),
    ('lowprice', "Выводит топ самых дешевых отелей в указанном городе"),
    ('highprice', "Выводит топ самых дорогих отелей в указанном городе"),
    ('bestdeal', "Выводит топ отелей, наиболее подходящих по цене и расположению от центра "
                 "(самые дешёвые и находятся ближе всего к центру)"),
    ('history', "Выводит историю поиска по отелям")
)
