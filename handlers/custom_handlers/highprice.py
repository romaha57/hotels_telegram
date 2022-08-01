import datetime
from telebot.types import Message, CallbackQuery
from loader import bot
from states.UserStateHigh import UserStateHigh
from keyboards.inline.question_photo_high import question_photo_high
from keyboards.inline.accept_info_high import accept_info_high
from keyboards.reply.again_button_high import start_again_high
from parser_API.parser import requests_to_api, get_hotels


@bot.message_handler(commands=['highprice'])
def start_high(message: Message) -> None:
    """Функция для запроса города для поиска"""

    # Удаления состояния finish при переходе из других сценариев
    bot.delete_state(message.from_user.id, message.chat.id)

    # Установка состояния для города
    bot.set_state(message.from_user.id, UserStateHigh.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите город для поиска отелей:')


@bot.message_handler(state=UserStateHigh.city)
def get_city_high(message: Message) -> None:
    """Функция, для запроса количества отелей"""

    if not message.text.isdigit():
        bot.send_message(message.from_user.id, 'Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, UserStateHigh.hotel_count, message.chat.id)

        # получение доступа к данным, заданным в состояниях
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=UserStateHigh.hotel_count)
def hotel_count_high(message: Message) -> None:
    """Функция, для запроса даты  """

    if message.text.isdigit():
        text = 'Отлично, теперь укажите даты бронирования отеля(формат: дд-мм-гггг/дд-мм-гггг)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, UserStateHigh.date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


@bot.message_handler(state=UserStateHigh.date)
def date_high(message: Message) -> None:
    """Функция, для распознования вводимой даты и вопроса о выводе фото"""

    dates = message.text.split('/')
    try:
        # Проверка вводимой даты на шаблон и обработка ошибки

        check_in = datetime.datetime.strptime(str(dates[0]), '%d-%m-%Y')
        check_out = datetime.datetime.strptime(str(dates[1]), '%d-%m-%Y')
        days = check_out - check_in
        bot.send_message(message.from_user.id, 'Вывести результат поиска с фото?'
                         , reply_markup=question_photo_high())
        bot.set_state(message.from_user.id, UserStateHigh.photo_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['date'] = (dates[0], dates[1], days.days)

    except Exception:
        bot.send_message(message.from_user.id, 'Ошибка ввода даты.Попробуйте еще раз')


@bot.callback_query_handler(func=lambda call: call.data == 'yes1' or call.data == 'no1')
def callback_inline_high(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'yes1':
            bot.send_message(call.message.chat.id, 'Введите количество фото для отображения')
        elif call.data == 'no1':
            with bot.retrieve_data(call.message.chat.id) as data:
                pass
            text = 'Давайте проверим введенные данные:\n' \
                   f'\nГород: {data["city_name"]}' \
                   f'\nКоличество отелей на экране: {data["hotels_count"]}' \
                   f'\nЗаезд: {data["date"][0]}' \
                   f'\nВыезд: {data["date"][1]}' \
                   f'\nДней всего: {data["date"][2]}'\
                   f'\n\nВсе верно?'

            bot.send_message(call.message.chat.id, text, reply_markup=accept_info_high())


@bot.message_handler(state=UserStateHigh.photo_count)
def photo_count_high(message: Message) -> None:
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

        bot.send_message(message.from_user.id, text, reply_markup=accept_info_high())
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')
    bot.set_state(message.from_user.id, UserStateHigh.finish, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'show_result1' or call.data == 'again1')
def callback_func_high(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'show_result1':
           show_hotels_high(call.message)

        elif call.data == 'again1':
            bot.send_message(call.message.chat.id, 'Тогда давайте введем данные заново,'
                                                   'Для этого нажмите на кнопку', reply_markup=start_again_high())


def show_hotels_high(message):
    """Функция для подключения к API-hotels и обработки ошибок при подключении"""

    bot.send_message(message.chat.id, 'Отлично, начинаем поиск(это может занять некоторое время...)')
    bot.send_message(message.chat.id, 'Подключаемся к базе данных отеля в указанном городе(1/3)...')
    with bot.retrieve_data(message.chat.id) as data:
        pass
    city_id = requests_to_api(data["city_name"])
    if city_id is not None:
        bot.send_message(message.chat.id, 'Получаем информацию по отелям(2/3)...')
        hotels = get_hotels(city_id=city_id, search_info="PRICE_HIGHEST_FIRST", count=data["hotels_count"])
        if hotels is not None:
            print_info_high(message, hotels)
        else:
            bot.send_message(message.chat.id, 'К сожалению, не удалось найти информацию по отелям')
    else:
        bot.send_message(message.chat.id, 'К сожалению, сервис с информацией по отелям временно не работает')


def print_info_high(message, hotels):
    """Функция для вывода информации по отелям в телеграмм(с заданными параметрами)"""

    with bot.retrieve_data(message.chat.id) as data:
        pass
    bot.send_message(message.chat.id, 'Результат поиска:')
    for i in range(int(data["hotels_count"])):
        total_cost = int(data["date"][2]) * float(hotels[i][2][1:])
        text = f'Название отеля: {hotels[i][0]}' \
           f'\nАдрес отеля: {hotels[i][3]}' \
           f'\nРасположение от центра: {hotels[i][6]}' \
           f'\nЦена за сутки: {hotels[i][2]}' \
           f'\nЦена всего: {total_cost}' \
           f'\nКоличество звезд отеля: {hotels[i][5]}' \
           f'\nРейтинг отеля: {hotels[i][4]}' \

        bot.send_message(message.chat.id, text)
    del hotels