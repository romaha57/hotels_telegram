from keyboards.reply.all_command import all_commands
from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """Функция при вводе команды /start"""

    text = """\nДоступные функции:\n
/lowprice - поиск самых дешевых отелей в выбранном городе 📈
/highprice - поиск самых дорогих отелей в выбранном городе 📉
/bestdeal - поиск отелей в выбранном ценовом диапазоне и удаленности от центра 🔝
/history - история поиска 📒
/favorite - избранные отели ❤
    \n<b>Для начала поиска выберите одну из функции</b>"""
    if message.chat.last_name is not None:
        bot.send_message(message.from_user.id, f'Здравствуйте, '
                                               f'{message.chat.first_name}{message.chat.last_name}😃'
                         + text, parse_mode='html',reply_markup=all_commands())
    bot.send_message(message.from_user.id, f'Здравствуйте, '
                                           f'{message.chat.first_name}😃 ' + text, parse_mode='html',
                     reply_markup=all_commands())


















