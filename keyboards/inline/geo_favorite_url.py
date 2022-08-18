from telebot import types


def geo_favorite_url(lat: int, lon: int, hotels: str,
                     city_name: str, hotel_id: int) -> types.InlineKeyboardMarkup:

    """Функция, которая выводит кнопку для отображения геолокации,
    добавление в избранное и ссылку на отель
    """

    # получаем название отеля
    hotel_name = hotels.split()

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    call_data = 'geo' + '/' + str(lat) + '/' + str(lon) + '/' + ' '.join(hotel_name[:4])
    geo_button = types.InlineKeyboardButton(text='📍 показать на карте', callback_data=call_data)

    # берем только первые 4 слова из названия отеля, чтобы поместить в callback_data
    call_data1 = 'favorite' + '/' + ' '.join(hotel_name[:4]) + '/' + city_name
    like_button = types.InlineKeyboardButton(text='❤ Добавить в избранное ',
                                             callback_data=call_data1)

    # создаем ссылку на отель
    url_button = types.InlineKeyboardButton(text='📲 Забронировать',
                                            url=f'https://www.hotels.com/ho{hotel_id}')

    keyboard.add(geo_button, like_button, url_button)

    return keyboard
