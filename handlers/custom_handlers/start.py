from telebot.types import Message
from loguru import logger

from keyboards.reply.all_command import all_commands
from loader import bot
from utils.my_log import debug_log_write, warning_log_write

# вызываем функции для создания логов
debug_log_write()
warning_log_write()


@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """Функция при вводе команды /start"""

    logger.debug('Отловили команду start')

    text = """\nДоступные функции:\n
/lowprice - поиск дешевых отелей в выбранном городе 📈
/highprice - поиск дорогих отелей в выбранном городе 📉
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


















