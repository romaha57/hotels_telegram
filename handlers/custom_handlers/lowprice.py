import datetime
from telebot.types import Message
from loader import bot
from states.lowhighprice import LowHighPrice
from keyboards.inline.question_photo import question_photo
from keyboards.inline.accept_info import accept_info
from keyboards.reply.again_button import start_again
from parser_API.parser import requests_to_api, get_hotels


@bot.message_handler(commands=['lowprice'])
def start(message: Message) -> None:
    """Функция для запроса города для поиска"""

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, LowHighPrice.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите город для поиска отелей:')


@bot.message_handler(state=LowHighPrice.city)
def get_city(message: Message) -> None:
    """Функция, для запроса количества отелей"""
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, LowHighPrice.hotel_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=LowHighPrice.hotel_count)
def hotel_count(message: Message) -> None:
    """Функция, для запроса даты  """

    if message.text.isdigit():
        text = 'Отлично, теперь укажите даты бронирования отеля(формат: дд-мм-гггг/дд-мм-гггг)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, LowHighPrice.date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


@bot.message_handler(state=LowHighPrice.date)
def date(message: Message) -> None:
    """Функция, для распознования вводимой даты и вопроса о выводе фото"""

    dates = message.text.split('/')
    try:
        check_in = datetime.datetime.strptime(str(dates[0]), '%d-%m-%Y')
        check_out = datetime.datetime.strptime(str(dates[1]), '%d-%m-%Y')
        days = check_out - check_in
        bot.send_message(message.from_user.id, 'Вывести результат поиска с фото?'
                         , reply_markup=question_photo())
        bot.set_state(message.from_user.id, LowHighPrice.photo_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['date'] = (dates[0], dates[1], days.days)

    except:
        bot.send_message(message.from_user.id, 'Ошибка ввода даты.Попробуйте еще раз')


@bot.callback_query_handler(func=lambda call: call.data == 'yes' or call.data == 'no')
def callback_inline(call):
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

            bot.send_message(call.message.chat.id, text, reply_markup=accept_info())


@bot.message_handler(state=LowHighPrice.photo_count)
def photo_count(message: Message) -> None:
    """Функция, для подтверждения информации"""

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

        bot.send_message(message.from_user.id, text, reply_markup=accept_info())
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')
    bot.set_state(message.from_user.id, LowHighPrice.finish, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'show_result' or call.data == 'again')
def callback_func(call):
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'show_result':
           show_hotels(call.message)

        elif call.data == 'again':
            bot.send_message(call.message.chat.id, 'Тогда давайте введем данные заново,'
                                                   'Для этого нажмите на кнопку', reply_markup=start_again())


def show_hotels(message):
    bot.send_message(message.chat.id, 'Отлично, начинаем поиск(это может занять некоторое время...)')
    bot.send_message(message.chat.id, 'Подключаемся к базе данных отеля в указанном городе(1/3)...')
    with bot.retrieve_data(message.chat.id) as data:
        pass
    city_id = requests_to_api(data["city_name"])
    if city_id is not None:
        bot.send_message(message.chat.id, 'Получаем информацию по отелям(2/3)...')
        hotels = get_hotels(city_id, 'PRICE', data["hotels_count"])
        if hotels is not None:
            print_info(message, hotels)
        else:
            bot.send_message(message.chat.id, 'К сожалению, не удалось найти информацию по отелям')
    else:
        bot.send_message(message.chat.id, 'К сожалению, сервис с информацией по отелям временно не работает')


def print_info(message, hotels):
    with bot.retrieve_data(message.chat.id) as data:
        pass
    bot.send_message(message.chat.id, 'Результат поиска:')
    for i in range(int(data["hotels_count"])):
        total_cost = int(data["date"][2]) * int(hotels[i][2][1:])
        text = f'Название отеля: {hotels[i][0]}' \
           f'\nАдрес отеля: {hotels[i][3]}' \
           f'\nРасположение от центра: {hotels[i][6]}' \
           f'\nЦена за сутки: {hotels[i][2]}' \
           f'\nЦена всего: {total_cost}' \
           f'\nКоличество звезд отеля: {hotels[i][5]}' \
           f'\nРейтинг отеля: {hotels[i][4]}' \

        bot.send_message(message.chat.id, text)
