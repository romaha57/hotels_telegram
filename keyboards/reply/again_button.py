from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def start_again() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('/lowprice'))
    return keyboard