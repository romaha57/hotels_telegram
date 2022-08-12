from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """Функция при вводе команды /start"""

    text = """\nДоступные функции:\n
    /lowprice - поиск самых дешевые отели в выбранном городе 📈
    /highprice - поиск самых дорогие отели в выбранном городе 📉
    /bestdeal - поиск отелей в выбранном ценновом диапозоне и удаленности от центра 🔝
    /history - история поиска 📒
    \n<b>Для начала поиска выберите одну из функции</b>"""
    if message.chat.last_name is not None:
        bot.send_message(message.from_user.id, f'Здравствуйте, '
                                               f'{message.chat.first_name}{message.chat.last_name}😃'
                         + text, parse_mode='html')
    bot.send_message(message.from_user.id, f'Здравствуйте, '
                                           f'{message.chat.first_name}😃 ' + text, parse_mode='html')


















