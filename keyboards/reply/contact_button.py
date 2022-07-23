from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def requsts_contact() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('Отправить контакт', request_contact=True))
    return keyboard