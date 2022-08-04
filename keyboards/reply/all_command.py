from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def all_commands() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    lowprice = KeyboardButton('/lowprice')
    highprice = KeyboardButton('/highprice')
    bestdeal = KeyboardButton('/bestdeal')
    history = KeyboardButton('/history')
    help = KeyboardButton('/help')
    keyboard.add(lowprice, highprice, bestdeal, history, help)

    return keyboard
