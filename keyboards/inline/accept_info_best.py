from telebot import types


def accept_info_best() -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопки для подтверждения информации для поиска"""

    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text='Да', callback_data='show_result2')
    no = types.InlineKeyboardButton(text='Нет', callback_data='again2')
    markup.add(yes, no)
    return markup