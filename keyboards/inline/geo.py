from telebot import types


def geo(lat: int, lon: int) -> types.InlineKeyboardMarkup:
    """Функция, которая выводит кнопку для отображения геолокации"""

    keyboard = types.InlineKeyboardMarkup()
    call_data = 'geo' + '/' + str(lat) + '/' + str(lon)
    geo_button = types.InlineKeyboardButton(text='📍 показать на карте', callback_data=call_data)
    keyboard.add(geo_button)

    return keyboard
