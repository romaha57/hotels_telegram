from telebot import types


def accept_info() -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопки для подтверждения информации"""

    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(yes, no)
    return markup