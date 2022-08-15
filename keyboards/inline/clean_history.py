from telebot import types


def clean_history_button() -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопку для удаления истории поиска"""

    keyboard = types.InlineKeyboardMarkup()
    clean_history_but = types.InlineKeyboardButton(text='❌ Для удаления истории нажмите',
                                                   callback_data='clean_history')
    keyboard.add(clean_history_but)

    return keyboard
