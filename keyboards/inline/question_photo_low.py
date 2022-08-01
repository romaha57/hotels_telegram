from telebot import types


def question_photo_low() -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопки для запроса фото"""

    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    markup.add(yes, no)
    return markup