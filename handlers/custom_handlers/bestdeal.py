import datetime
from telebot.types import Message, CallbackQuery

from keyboards.reply.again_button_best import start_again_best
from loader import bot
from parser_API.parser import requests_to_api, get_hotels_bestdeal
from states.UserStateBest import BestDealInfo
from keyboards.inline.question_photo_best import question_photo_best
from keyboards.inline.accept_info_best import accept_info_best


@bot.message_handler(commands=['bestdeal'])
def start(message: Message) -> None:
    """Функция для запроса города для поиска"""

    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, BestDealInfo.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Укажите город для поиска отелей:')


@bot.message_handler(state=BestDealInfo.city)
def get_city(message: Message) -> None:
    """Функция, для запроса диапозона цен"""

    if not message.text.isdigit():
        text = 'Теперь укажите диапозон цен отелей(пример: 100-500)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, BestDealInfo.price_range, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city_name'] = message.text.title()
    else:
        bot.send_message(message.from_user.id, 'Название города должно состоять из букв')


@bot.message_handler(state=BestDealInfo.price_range)
def hotel_count(message: Message) -> None:
    """Функция, для запроса диапозона расстояния от центра  """

    try:
        prices = message.text.split('-')
        start_price = int(prices[0])
        stop_price = int(prices[1])
        text = 'Отлично, теперь укажите диапозон расстояния от центра(пример: 0.5-5)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, BestDealInfo.dist_range, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['prices'] = (start_price, stop_price)

    except Exception:
        bot.send_message(message.from_user.id, 'Некорректный ввод.Попробуйте еще раз')


@bot.message_handler(state=BestDealInfo.dist_range)
def date(message: Message) -> None:
    """Функция, для запроса количества отелей """

    try:
        dists = message.text.split('-')
        start_dist = int(dists[0])
        stop_dist = int(dists[1])
        bot.send_message(message.from_user.id, 'Теперь укажите количество отелей для вывода на экран:')
        bot.set_state(message.from_user.id, BestDealInfo.hotel_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_range'] = (start_dist, stop_dist)

    except:
        bot.send_message(message.from_user.id, 'Ошибка ввода.Попробуйте еще раз')


@bot.message_handler(state=BestDealInfo.hotel_count)
def hotel_count(message: Message) -> None:
    """Функция, для запроса даты  """

    if message.text.isdigit():
        text = 'Отлично, теперь укажите даты бронирования отеля(формат: дд-мм-гггг/дд-мм-гггг)'
        bot.send_message(message.from_user.id, text)
        bot.set_state(message.from_user.id, BestDealInfo.date, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['hotels_count'] = message.text
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, цифрами')


@bot.message_handler(state=BestDealInfo.date)
def date(message: Message) -> None:
    """Функция, для распознования вводимой даты и вопроса о выводе фото"""

    dates = message.text.split('/')
    try:
        check_in = datetime.datetime.strptime(str(dates[0]), '%d-%m-%Y')
        check_out = datetime.datetime.strptime(str(dates[1]), '%d-%m-%Y')
        days = check_out - check_in
        bot.send_message(message.from_user.id, 'Вывести результат поиска с фото?'
                         , reply_markup=question_photo_best())
        bot.set_state(message.from_user.id, BestDealInfo.photo_count, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['date'] = (dates[0], dates[1], days.days)

    except Exception:
        bot.send_message(message.from_user.id, 'Ошибка ввода даты.Попробуйте еще раз')


@bot.callback_query_handler(func=lambda call: call.data == 'yes2' or call.data == 'no2')
def callback_inline(call):
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'yes2':
            bot.send_message(call.message.chat.id, 'Введите количество фото для отображения')
        elif call.data == 'no2':
            with bot.retrieve_data(call.message.chat.id) as data:
                pass
            text = 'Давайте проверим введенные данные:\n' \
                   f'\nГород: {data["city_name"]}' \
                   f'\nКоличество отелей на экране: {data["hotels_count"]}' \
                   f'\nДиапозон цен: от {data["prices"][0]} до {data["prices"][1]}' \
                   f'\nДиапозон расстояния от центра: от {data["dist_range"][0]} до {data["dist_range"][1]}' \
                   f'\nЗаезд: {data["date"][0]}' \
                   f'\nВыезд: {data["date"][1]}' \
                   f'\nДней всего: {data["date"][2]}' \
                   f'\n\nВсе верно?'

            bot.send_message(call.message.chat.id, text, reply_markup=accept_info_best())


@bot.message_handler(state=BestDealInfo.photo_count)
def photo_count(message: Message) -> None:
    """Функция, для подтверждения информации"""

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photo_count'] = message.text

        text = 'Давайте проверим введенные данные:\n' \
               f'\nГород: {data["city_name"]}' \
               f'\nДиапозон цен: от {data["prices"][0]} до {data["prices"][1]}' \
               f'\nДиапозон расстояния от центра: от {data["dist_range"][0]} до {data["dist_range"][1]}'\
               f'\nКоличество отелей на экране: {data["hotels_count"]}' \
               f'\nЗаезд: {data["date"][0]}' \
               f'\nВыезд: {data["date"][1]}' \
               f'\nДней всего: {data["date"][2]}' \
               f'\nФото штук: {data["photo_count"]}' \
               f'\n\nВсе верно?' \

        bot.send_message(message.from_user.id, text, reply_markup=accept_info_best())
    else:
        bot.send_message(message.from_user.id, 'Введите, пожалуйста, число')
    bot.set_state(message.from_user.id, BestDealInfo.finish, message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data == 'show_result2' or call.data == 'again2')
def callback_func(call: CallbackQuery) -> None:
    """Обработчик inline-кнопок """

    if call.message:
        if call.data == 'show_result2':
           show_hotels(call.message)

        elif call.data == 'again2':
            bot.send_message(call.message.chat.id, 'Тогда давайте введем данные заново,'
                                                   'Для этого нажмите на кнопку', reply_markup=start_again_best())


def show_hotels(message):
    """Функция для подключения к API-hotels и обработки ошибок при подключении"""

    bot.send_message(message.chat.id, 'Отлично, начинаем поиск(это может занять некоторое время...)')
    bot.send_message(message.chat.id, 'Подключаемся к базе данных отеля в указанном городе(1/3)...')
    with bot.retrieve_data(message.chat.id) as data:
        pass
    city_id = requests_to_api(data["city_name"])
    if city_id is not None:
        bot.send_message(message.chat.id, 'Получаем информацию по отелям(2/3)...')
        hotels = get_hotels_bestdeal(city_id=city_id,
                                     search_info="DISTANCE_FROM_LANDMARK",
                                     count=data["hotels_count"],
                                     start_price=data["prices"][0],
                                     stop_price=data["prices"][1],
                                     start_dist=data["dist_range"][0],
                                     stop_dist=data["dist_range"][1],
                                     bestdeal_list=[])
        print(hotels)

        if hotels is not None:
            print_info(message, hotels)
        else:
            bot.send_message(message.chat.id, 'К сожалению, не удалось найти информацию по отелям')
    else:
        bot.send_message(message.chat.id, 'К сожалению, сервис с информацией по отелям временно не работает')


def print_info(message, hotels):
    """Функция для вывода информации по отелям в телеграмм(с заданными параметрами)"""

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
    del hotels