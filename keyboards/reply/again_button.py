from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def start_again(command: str) -> ReplyKeyboardMarkup:
    """Кнопки для повторного ввода команды,
    если при вводе информация пользователь допустил ошибку"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton(f'{command}'))

    return keyboard
