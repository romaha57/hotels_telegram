from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def all_commands() -> ReplyKeyboardMarkup:
    """Кнопки после выдачи результата поиска, для выбора следующей команды"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    lowprice = KeyboardButton('/lowprice')
    highprice = KeyboardButton('/highprice')
    bestdeal = KeyboardButton('/bestdeal')
    history = KeyboardButton('/history')
    help = KeyboardButton('/help')
    favorite = KeyboardButton('/favorite')
    keyboard.add(lowprice, highprice, bestdeal, history, help, favorite)

    return keyboard
