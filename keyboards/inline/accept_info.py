from telebot import types


def accept_info() -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопки для подтверждения информации для поиска"""

    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text='Да', callback_data='show_result')
    no = types.InlineKeyboardButton(text='Нет', callback_data='again')
    markup.add(yes, no)
    return markup