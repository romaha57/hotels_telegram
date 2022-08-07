from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def start_again_low() -> ReplyKeyboardMarkup:
    """Кнопки для повторного ввода команды lowprice,
       если при вводе информация пользователь допустил ошибку"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('/lowprice'))

    return keyboard
