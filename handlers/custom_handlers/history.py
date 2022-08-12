from loader import bot
from telebot.types import Message
from database.my_db import get_info_from_database, close_connect
from states.UserStateHistory import UserStateHistory


@bot.message_handler(commands=['history'])
def start(message: Message):
    bot.set_state(message.from_user.id, UserStateHistory.limit, message.chat.id)
    bot.send_message(message.chat.id, 'Сколько записей истории вывести на экран?')


@bot.message_handler(state=UserStateHistory.limit)
def show_history(message: Message):
    """Функция, для вывода информации из БД"""

    if message.text.isdigit():

        # Установка LIMIT для SELECT- запроса с БД
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["limit"] = message.text

        bot.set_state(message.from_user.id, UserStateHistory.finish, message.chat.id)

        bot.send_message(message.from_user.id, 'Подгружаем историю поиска...')
        info = get_info_from_database(message.from_user.id, data["limit"])

        # Берем инфомармацию по отелям и делаем читабельный вид
        for element in info:
            # Преобразовываем записи отелей из БД в отдельные элементы
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
                    text = ''

                    # делаем одну большую строку для вывода информации
                hotels += text
            text = f'\n<b>Дата и время:</b> {element[2]}' \
                   f'\n\n<b>Команда:</b> {element[3]}' \
                   f'\n\n<b>Отели:</b> \n{hotels}'
            bot.send_message(message.from_user.id, text, parse_mode='html')

        # Вызываем функцию для закрытия коннекта с БД
        close_connect()

    else:
        bot.send_message(message.chat.id, 'Некорректный ввод. Введите число')