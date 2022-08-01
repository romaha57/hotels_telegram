from telebot import types


def accept_info_high() -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопки для подтверждения информации для поиска"""

    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text='Да', callback_data='show_result1')
    no = types.InlineKeyboardButton(text='Нет', callback_data='again1')
    markup.add(yes, no)
    return markup