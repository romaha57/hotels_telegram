from telebot import types


def question_photo_best() -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопки для запроса фото"""

    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(text='Да', callback_data='yes2')
    no = types.InlineKeyboardButton(text='Нет', callback_data='no2')
    markup.add(yes, no)
    return markup