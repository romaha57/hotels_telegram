import datetime
from telebot.types import Message, CallbackQuery
from typing import List, Tuple
from keyboards.reply.all_command import all_commands
from loader import bot
from states.UserStateLow import UserStateLow
from keyboards.inline.question_photo_low import question_photo_low
from keyboards.inline.accept_info_low import accept_info_low
from keyboards.reply.again_button_low import start_again_low
from parser_API.parser import requests_to_api, get_hotels
from database.my_db import add_in_db


@bot.message_handler(commands=['lowprice'])
def start(message: Message) -> None:
    """Функция для запроса города для поиска"""

    # Удаления состояния finish при переходе из других сценариев
    bot.delete_state(message.from_user.id, message.chat.id)
    # Установка состояния для города
    bot.set_state(message.from_user.id, UserStateLow.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите город для поиска отелей:')


@bot.message_handler(state=UserStateLow.city)
def get_city(message: Message) -> None:
    """Функция, для запроса количества отелей"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id,
                         'Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, UserStateLow.hotel_count, message.chat.id)

        # получение доступа к данным, заданным в состояниях
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=UserStateLow.hotel_count)
def hotel_count(message: Message) -> None:
    """Функция, для запроса даты  """

    if message.text.isdigit():
        text = 'Отлично, теперь укажите даты бронирования отеля(формат: дд-мм-гггг/дд-мм-гггг)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, UserStateLow.date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


@bot.message_handler(state=UserStateLow.date)
def date(message: Message) -> None:
    """Функция, для распознавания вводимой даты и вопроса о выводе фото"""

    dates = message.text.split('/')
    try:
        # Проверка вводимой даты на шаблон и обработка ошибки

        check_in = datetime.datetime.strptime(str(dates[0]), '%d-%m-%Y')
        check_out = datetime.datetime.strptime(str(dates[1]), '%d-%m-%Y')
        days = check_out - check_in
        bot.send_message(message.from_user.id, 'Вывести результат поиска с фото?'
                         , reply_markup=question_photo_low())
        bot.set_state(message.from_user.id, UserStateLow.photo_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['date'] = (dates[0], dates[1], days.days)

    except Exception:
        bot.send_message(message.from_user.id, 'Ошибка ввода даты.Попробуйте еще раз')


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def callback_inline(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'yes':
            bot.send_message(call.message.chat.id, 'Введите количество фото для отображения')
        elif call.data == 'no':
            with bot.retrieve_data(call.message.chat.id) as data:
                pass
            text = 'Давайте проверим введенные данные:\n' \
                   f'\nГород: {data["city_name"]}' \
                   f'\nКоличество отелей на экране: {data["hotels_count"]}' \
                   f'\nЗаезд: {data["date"][0]}' \
                   f'\nВыезд: {data["date"][1]}' \
                   f'\nДней всего: {data["date"][2]}'\
                   f'\n\nВсе верно?'

            bot.send_message(call.message.chat.id, text, reply_markup=accept_info_low())


@bot.message_handler(state=UserStateLow.photo_count)
def photo_count(message: Message) -> None:
    """Функция, для подтверждения информации"""

    bot.set_state(message.from_user.id, UserStateLow.finish, message.chat.id)
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_count'] = message.text

        text = 'Давайте проверим введенные данные:\n' \
               f'\nГород: {data["city_name"]}' \
               f'\nКоличество отелей на экране: {data["hotels_count"]}' \
               f'\nЗаезд: {data["date"][0]}' \
               f'\nВыезд: {data["date"][1]}' \
               f'\nДней всего: {data["date"][2]}' \
               f'\nФото штук: {data["photo_count"]}' \
               f'\n\nВсе верно?' \

        bot.send_message(message.from_user.id, text, reply_markup=accept_info_low())
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')


@bot.callback_query_handler(func=lambda call: call.data == 'show_result' or call.data == 'again')
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'show_result':
           show_hotels(call.message)

        elif call.data == 'again':
            bot.send_message(call.message.chat.id, 'Тогда давайте введем данные заново,'
                                                   'Для этого нажмите на кнопку',
                             reply_markup=start_again_low())


def show_hotels(message: Message) -> None:
    """Функция для подключения к API-hotels и обработки ошибок при подключении"""

    bot.send_message(message.chat.id, 'Отлично, начинаем поиск(это может занять некоторое время...)')
    bot.send_message(message.chat.id, 'Подключаемся к базе данных отеля в указанном городе(1/3)...')
    with bot.retrieve_data(message.chat.id) as data:
        pass
    city_id = requests_to_api(data["city_name"])
    if city_id is not None:
        bot.send_message(message.chat.id, 'Получаем информацию по отелям(2/3)...')

        # запрос для вывода информации по отелям с командой lowprice
        hotels = get_hotels(city_id=city_id, search_info="PRICE", count=data["hotels_count"])
        if hotels is not None:
            # если ошибок нет переходим в функцию вывода информации по отелям
            print_info(message, hotels)
        else:
            bot.send_message(message.chat.id, 'К сожалению, не удалось найти информацию по отелям')
    else:
        bot.send_message(message.chat.id,
                         'К сожалению, сервис с информацией по отелям временно не работает')


def print_info(message: Message, hotels: List[Tuple]) -> None:
    """Функция для вывода информации по отелям в телеграмм(с заданными параметрами)"""

    with bot.retrieve_data(message.chat.id) as data:
        pass
    bot.send_message(message.chat.id, 'Результат поиска:')
    for i in range(int(data["hotels_count"])):

        # подсчет общей стоимости отеля
        total_cost = round(int(data["date"][2]) * int(hotels[i][2][1:]), 2)
        text = f'Название отеля: {hotels[i][1]}' \
           f'\nАдрес отеля: {hotels[i][3]}' \
           f'\nРасположение от центра: {hotels[i][6]}' \
           f'\nЦена за сутки: {hotels[i][2]}' \
           f'\nЦена всего: {total_cost}' \
           f'\nКоличество звезд отеля: {hotels[i][5]}' \
           f'\nРейтинг отеля: {hotels[i][4]}' \

        bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, 'Выберите одну из функции:', reply_markup=all_commands())
    bot.register_next_step_handler(message, add_in_database, hotels)

    # Удаление списка отеля(думаю так должно быстрее работать и не занимать лишнюю память)
    del hotels


def add_in_database(message: Message, hotels: List[Tuple]) -> None:
    """Функция, для передачи данных для записи в БД"""

    # текущая дата и время
    date = datetime.datetime.now()
    date = str(date)

    users_tuple = (message.from_user.id, date[:-6], 'lowprice')
    add_in_db(users_info=users_tuple, hotels=hotels)


