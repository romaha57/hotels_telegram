from telebot import types


def delete_history(id_string: str, message_id: int) -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопку для отображения геолокации"""

    keyboard = types.InlineKeyboardMarkup()
    call_data = '///' + id_string + '///' + str(message_id) + '///'
    del_button = types.InlineKeyboardButton(text='Удалить запись', callback_data=call_data)
    keyboard.add(del_button)

    return keyboard
