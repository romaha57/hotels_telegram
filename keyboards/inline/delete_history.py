from telebot import types


def delete_history(id_string: str, message_id: int, command: str) -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопку для удаления записи в БД"""

    keyboard = types.InlineKeyboardMarkup()
    call_data = '///' + id_string + '///' + str(message_id) + '///' + command
    del_button = types.InlineKeyboardButton(text='Удалить запись', callback_data=call_data)
    keyboard.add(del_button)

    return keyboard
