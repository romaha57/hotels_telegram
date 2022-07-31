from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:

    text = """\nВас приветствует EasyTravelBot для поиска отеля в любой точке мира 🌍
    \nДоступные функции:
    /lowprice - покажет самые дешевые отели в выбранном городе
    /highprice - покажет самые дорогие отели в выбранном городе
    /bestdeal - лучшие предложения на рынке
    /history - история поиска
    \n Для начала поиска выберите одну из функции"""
    if not message.chat.last_name is None:
        bot.send_message(message.from_user.id, f'Здравствуйте, '
                                           f'{message.chat.first_name}{message.chat.last_name}😃 ' + text)
    bot.send_message(message.from_user.id, f'Здравствуйте, '
                                           f'{message.chat.first_name}😃 ' + text)


















