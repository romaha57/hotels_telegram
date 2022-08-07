from loader import bot
from database.my_db import get_info_from_database, close_connect


@bot.message_handler(commands=['history'])
def history(message):
    """Функция, для вывода информации из БД"""

    bot.send_message(message.from_user.id, 'Подгружаем историю поиска...')
    info = get_info_from_database(message.from_user.id)

    # Берем инфомармацию по отелям и делаем читабельный вид
    for element in info:
        x = element[4].split('\t\t')
        hotels = ''
        for el in x:
            y = el.split('%')
            try:
                text = f'\n\nНазвание: {y[1]}' \
                       f'\nЦена за сутки: {y[2]}'\
                       f'\nАдрес отеля: {y[3]}'\
                       f'\nРейтинг отеля: {y[4]}' \
                       f'\nКоличество звезд: {y[5]}' \
                       f'\nРасстояние от центра: {y[6]}'
            except IndexError:
                pass
            hotels += text
        text = f'\n<b>Дата и время:</b> {element[2]}' \
               f'\n\n<b>Команда:</b> {element[3]}' \
               f'\n\n<b>Отели:</b> \n{hotels}'
        bot.send_message(message.from_user.id, text, parse_mode='html')

    # Вызываем функцию для закрытия коннекта с БД
    close_connect()
